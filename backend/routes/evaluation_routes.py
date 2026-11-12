"""Internal E-Governance Portal Evaluation & Audit Module (Restricted Administration)."""
import json
import uuid
from datetime import datetime
from io import BytesIO
from flask import Blueprint, g, jsonify, request, send_file
from backend.auth import auth_required, error
from backend.database import connect_db, now_iso, row_dict
from backend.pdf_service import build_evaluation_report_pdf

evaluation_bp = Blueprint("evaluations", __name__, url_prefix="/api")

EVALUATION_CRITERIA = [
    "User Friendliness", "Navigation and Interface", "Accessibility", "Service Availability",
    "Application Process", "Application Tracking", "Information Accuracy", "Security and Privacy",
    "Mobile Responsiveness", "Overall User Experience"
]

EVALUATION_FIELDS = [
    "portal_name", "portal_url", "department", "description", "evaluation_date",
    "evaluator_group", "strengths", "limitations", "technical_issues", "user_difficulties",
    "improvements", "priority", "expected_benefits", "recommendations"
]

def format_evaluation_view(row) -> dict:
    item = row_dict(row)
    try:
        item["scores"] = json.loads(item["scores"])
    except Exception:
        item["scores"] = {}
    return item

@evaluation_bp.get("/evaluations")
@auth_required("admin")
def list_evaluations():
    q = request.args.get("q", "").strip()
    with connect_db() as db:
        if q:
            rows = db.execute(
                "SELECT * FROM evaluations WHERE portal_name LIKE ? OR evaluator_group LIKE ? ORDER BY created_at DESC LIMIT 50",
                (f"%{q}%", f"%{q}%")
            ).fetchall()
        else:
            rows = db.execute("SELECT * FROM evaluations ORDER BY created_at DESC LIMIT 50").fetchall()
    return jsonify([format_evaluation_view(r) for r in rows])

@evaluation_bp.get("/evaluations/<eval_id>")
@auth_required("admin")
def get_evaluation(eval_id):
    with connect_db() as db:
        row = db.execute("SELECT * FROM evaluations WHERE id=?", (eval_id,)).fetchone()
    item = format_evaluation_view(row) if row else None
    return (jsonify(item), 200) if item else error("Evaluation record not found.", 404)

@evaluation_bp.post("/evaluations")
@auth_required()
def create_evaluation():
    data = request.get_json(silent=True) or {}
    scores = data.get("scores") or {}

    portal_name = str(data.get("portal_name", "")).strip()
    if len(portal_name) < 2:
        return error("Please select or specify the portal evaluated.")

    # Validate all 10 criteria
    checked_scores = {}
    for crit in EVALUATION_CRITERIA:
        val = scores.get(crit)
        try:
            val_int = int(val)
            if val_int < 1 or val_int > 5:
                raise ValueError()
            checked_scores[crit] = val_int
        except (TypeError, ValueError):
            return error(f"Please provide a rating between 1 and 5 for parameter: '{crit}'.")

    values = {f: str(data.get(f, "")).strip()[:3000] for f in EVALUATION_FIELDS}
    values["evaluation_date"] = values["evaluation_date"] or datetime.now().date().isoformat()
    values["priority"] = values["priority"] if values["priority"] in ("Low", "Medium", "High") else "Medium"

    eval_id = str(uuid.uuid4())
    stamp = now_iso()

    with connect_db() as db:
        db.execute(
            """INSERT INTO evaluations
            (id, portal_name, portal_url, department, description, evaluation_date, evaluator_group,
             scores, strengths, limitations, technical_issues, user_difficulties, improvements,
             priority, expected_benefits, recommendations, evaluator, created_by, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (eval_id, values["portal_name"], values["portal_url"], values["department"], values["description"],
             values["evaluation_date"], values["evaluator_group"], json.dumps(checked_scores),
             values["strengths"], values["limitations"], values["technical_issues"], values["user_difficulties"],
             values["improvements"], values["priority"], values["expected_benefits"], values["recommendations"],
             g.user["name"], g.user["id"], stamp)
        )
        row = db.execute("SELECT * FROM evaluations WHERE id=?", (eval_id,)).fetchone()

    return jsonify(format_evaluation_view(row)), 201

@evaluation_bp.put("/evaluations/<eval_id>")
@auth_required()
def update_evaluation(eval_id):
    data = request.get_json(silent=True) or {}
    scores = data.get("scores") or {}

    checked_scores = {}
    for crit in EVALUATION_CRITERIA:
        try:
            val = int(scores.get(crit, 0))
            if val < 1 or val > 5:
                raise ValueError()
            checked_scores[crit] = val
        except (TypeError, ValueError):
            return error(f"Please rate all 10 evaluation parameters from 1 to 5.")

    with connect_db() as db:
        existing = db.execute("SELECT * FROM evaluations WHERE id=?", (eval_id,)).fetchone()
        if not existing:
            return error("Evaluation record not found.", 404)
        if g.user["role"] != "admin" and existing["created_by"] != g.user["id"]:
            return error("You are only permitted to edit evaluations created by your account.", 403)

        values = {f: str(data.get(f, existing[f])).strip()[:3000] for f in EVALUATION_FIELDS}
        values["priority"] = values["priority"] if values["priority"] in ("Low", "Medium", "High") else "Medium"

        db.execute(
            """UPDATE evaluations SET
            portal_name=?, portal_url=?, department=?, description=?, evaluation_date=?, evaluator_group=?,
            scores=?, strengths=?, limitations=?, technical_issues=?, user_difficulties=?, improvements=?,
            priority=?, expected_benefits=?, recommendations=?
            WHERE id=?""",
            (values["portal_name"], values["portal_url"], values["department"], values["description"],
             values["evaluation_date"], values["evaluator_group"], json.dumps(checked_scores),
             values["strengths"], values["limitations"], values["technical_issues"], values["user_difficulties"],
             values["improvements"], values["priority"], values["expected_benefits"], values["recommendations"],
             eval_id)
        )
        row = db.execute("SELECT * FROM evaluations WHERE id=?", (eval_id,)).fetchone()

    return jsonify(format_evaluation_view(row))

@evaluation_bp.delete("/evaluations/<eval_id>")
@auth_required()
def delete_evaluation(eval_id):
    with connect_db() as db:
        row = db.execute("SELECT * FROM evaluations WHERE id=?", (eval_id,)).fetchone()
        if not row:
            return error("Evaluation record not found.", 404)
        if g.user["role"] != "admin" and row["created_by"] != g.user["id"]:
            return error("You are only permitted to delete your own evaluations.", 403)
        db.execute("DELETE FROM evaluations WHERE id=?", (eval_id,))
    return jsonify({"message": "Evaluation record deleted successfully."})

@evaluation_bp.get("/evaluations/<eval_id>/report.pdf")
@auth_required("admin")
def get_evaluation_report(eval_id):
    with connect_db() as db:
        row = db.execute("SELECT * FROM evaluations WHERE id=?", (eval_id,)).fetchone()
    if not row:
        return error("Evaluation record not found.", 404)

    item = format_evaluation_view(row)
    pdf_bytes = build_evaluation_report_pdf(item)
    return send_file(
        BytesIO(pdf_bytes),
        mimetype="application/pdf",
        as_attachment=True,
        download_name=f"Unit5-Evaluation-Report-{item['portal_name'].replace(' ', '_')}.pdf"
    )

# --- Group Management Routes ---

@evaluation_bp.get("/evaluation-groups")
@auth_required()
def list_groups():
    with connect_db() as db:
        rows = db.execute("SELECT * FROM evaluation_groups ORDER BY created_at DESC").fetchall()
    results = []
    for r in rows:
        d = row_dict(r)
        try:
            d["members"] = json.loads(d["members"])
        except Exception:
            d["members"] = []
        try:
            d["tasks"] = json.loads(d["tasks"])
        except Exception:
            d["tasks"] = []
        results.append(d)
    return jsonify(results)

@evaluation_bp.post("/evaluation-groups")
@auth_required()
def create_group():
    data = request.get_json(silent=True) or {}
    name = str(data.get("name", "")).strip()
    leader = str(data.get("leader", g.user["name"])).strip()
    members = data.get("members", [])
    tasks = data.get("tasks", [])

    if len(name) < 2:
        return error("Group name is required.")
    if not isinstance(members, list) or not isinstance(tasks, list):
        return error("Members and tasks must be formatted as lists.")

    group_id = str(uuid.uuid4())
    stamp = now_iso()
    clean_members = [str(m).strip()[:100] for m in members if str(m).strip()][:20]
    clean_tasks = [str(t).strip()[:300] for t in tasks if str(t).strip()][:30]

    with connect_db() as db:
        db.execute(
            """INSERT INTO evaluation_groups
            (id, name, leader, members, tasks, progress, created_by, created_at)
            VALUES (?, ?, ?, ?, ?, 0, ?, ?)""",
            (group_id, name, leader, json.dumps(clean_members), json.dumps(clean_tasks), g.user["id"], stamp)
        )

    return jsonify({
        "id": group_id,
        "name": name,
        "leader": leader,
        "members": clean_members,
        "tasks": clean_tasks,
        "progress": 0
    }), 201

@evaluation_bp.put("/evaluation-groups/<group_id>")
@auth_required()
def update_group(group_id):
    data = request.get_json(silent=True) or {}
    with connect_db() as db:
        group = db.execute("SELECT * FROM evaluation_groups WHERE id=?", (group_id,)).fetchone()
        if not group:
            return error("Group not found.", 404)
        if g.user["role"] != "admin" and group["created_by"] != g.user["id"]:
            return error("Only the group creator or an administrator can update this group.", 403)

        name = str(data.get("name", group["name"])).strip()[:150]
        leader = str(data.get("leader", group["leader"])).strip()[:100]
        members = data.get("members", json.loads(group["members"]))
        tasks = data.get("tasks", json.loads(group["tasks"]))
        try:
            progress = max(0, min(100, int(data.get("progress", group["progress"]))))
        except Exception:
            progress = group["progress"]

        db.execute(
            "UPDATE evaluation_groups SET name=?, leader=?, members=?, tasks=?, progress=? WHERE id=?",
            (name, leader, json.dumps(members), json.dumps(tasks), progress, group_id)
        )
        updated = db.execute("SELECT * FROM evaluation_groups WHERE id=?", (group_id,)).fetchone()

    d = row_dict(updated)
    d["members"] = json.loads(d["members"])
    d["tasks"] = json.loads(d["tasks"])
    return jsonify(d)

# --- Group Discussion Routes ---

@evaluation_bp.get("/evaluation-groups/<group_id>/discussions")
@auth_required()
def list_discussions(group_id):
    with connect_db() as db:
        rows = db.execute(
            "SELECT * FROM evaluation_discussions WHERE group_id=? ORDER BY created_at ASC",
            (group_id,)
        ).fetchall()
    return jsonify([row_dict(r) for r in rows])

@evaluation_bp.post("/evaluation-groups/<group_id>/discussions")
@auth_required()
def add_discussion(group_id):
    data = request.get_json(silent=True) or {}
    topic = str(data.get("topic", "Observation")).strip()[:100]
    message = str(data.get("message", "")).strip()[:2000]

    if not message:
        return error("Message content is required.")

    disc_id = str(uuid.uuid4())
    stamp = now_iso()
    with connect_db() as db:
        if not db.execute("SELECT 1 FROM evaluation_groups WHERE id=?", (group_id,)).fetchone():
            return error("Group not found.", 404)
        db.execute(
            """INSERT INTO evaluation_discussions (id, group_id, user_name, topic, message, created_at)
            VALUES (?, ?, ?, ?, ?, ?)""",
            (disc_id, group_id, g.user["name"], topic, message, stamp)
        )
        row = db.execute("SELECT * FROM evaluation_discussions WHERE id=?", (disc_id,)).fetchone()

    return jsonify(row_dict(row)), 201

# --- Presentation Support Routes ---

@evaluation_bp.get("/evaluation-groups/<group_id>/presentation")
@auth_required()
def get_presentation(group_id):
    with connect_db() as db:
        row = db.execute("SELECT * FROM evaluation_presentations WHERE group_id=?", (group_id,)).fetchone()
    return jsonify(row_dict(row) if row else {})

@evaluation_bp.put("/evaluation-groups/<group_id>/presentation")
@auth_required()
def save_presentation(group_id):
    data = request.get_json(silent=True) or {}
    title = str(data.get("title", "E-Governance Portal Evaluation Presentation")).strip()[:200]
    team_members = str(data.get("team_members", "")).strip()[:500]
    summary = str(data.get("summary", "")).strip()[:3000]
    key_findings = str(data.get("key_findings", "")).strip()[:3000]
    recommendations = str(data.get("recommendations", "")).strip()[:3000]

    pres_id = str(uuid.uuid4())
    stamp = now_iso()

    with connect_db() as db:
        if not db.execute("SELECT 1 FROM evaluation_groups WHERE id=?", (group_id,)).fetchone():
            return error("Group not found.", 404)
        existing = db.execute("SELECT id FROM evaluation_presentations WHERE group_id=?", (group_id,)).fetchone()
        if existing:
            db.execute(
                """UPDATE evaluation_presentations SET
                title=?, team_members=?, summary=?, key_findings=?, recommendations=?, updated_at=?
                WHERE group_id=?""",
                (title, team_members, summary, key_findings, recommendations, stamp, group_id)
            )
        else:
            db.execute(
                """INSERT INTO evaluation_presentations
                (id, group_id, title, team_members, summary, key_findings, recommendations, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
                (pres_id, group_id, title, team_members, summary, key_findings, recommendations, stamp)
            )
        row = db.execute("SELECT * FROM evaluation_presentations WHERE group_id=?", (group_id,)).fetchone()

    return jsonify(row_dict(row))

