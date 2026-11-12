/**
 * MP Suvidha: REST API Client
 */
async function api(path, options = {}) {
  const headers = new Headers(options.headers || {});

  if (State.token) {
    headers.set("Authorization", `Bearer ${State.token}`);
  }

  // Do not set Content-Type if body is FormData (let browser set multipart boundary)
  if (options.body && !(options.body instanceof FormData) && !headers.has("Content-Type")) {
    headers.set("Content-Type", "application/json");
  }

  const endpoint = path.startsWith("/api") ? path : `/api${path.startsWith("/") ? "" : "/"}${path}`;

  try {
    const response = await fetch(endpoint, { ...options, headers });
    const contentType = response.headers.get("content-type") || "";

    let body;
    if (contentType.includes("application/json")) {
      body = await response.json();
    } else {
      body = await response.text();
    }

    if (!response.ok) {
      const errorMsg = (typeof body === "object" && body !== null && body.error)
        ? body.error
        : `Request failed with status code ${response.status}.`;
      throw new Error(errorMsg);
    }

    return body;
  } catch (err) {
    throw err;
  }
}

