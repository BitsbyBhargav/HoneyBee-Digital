const base = (import.meta.env.VITE_API_URL || "").replace(/\/$/, "");
export const number = (value) =>
  new Intl.NumberFormat("en-IN").format(value ?? 0);

export async function get(path, signal) {
  let response;
  try {
    response = await fetch(`${base}/api${path}`, { signal });
  } catch (error) {
    if (error.name === "AbortError") throw error;
    throw new Error(
      "Cannot reach the API. Check that FastAPI is running, then try again.",
    );
  }
  if (!response.ok)
    throw new Error(
      `Could not load listings (${response.status}). Check the API and MySQL connection.`,
    );
  return response.json();
}
