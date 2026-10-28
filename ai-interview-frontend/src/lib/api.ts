
const API_BASE_URL =
  import.meta.env.VITE_API_BASE_URL || "http://127.0.0.1:8000";

export interface UserProfile {
  id: number;
  name: string;
  email: string;
  education: string | null;
  skills: string[];
  projects: string[];
  experience: string | null;
  target_role: string | null;
}


async function request<T>(
  path: string,
  options: RequestInit = {},
  token?: string,
): Promise<T> {
  const response = await fetch(`${API_BASE_URL}${path}`, {
    ...options,
    headers: {
      "Content-Type": "application/json",
      ...(token ? { Authorization: `Bearer ${token}` } : {}),
      ...options.headers,
    },
  });

  const data = await response.json().catch(() => ({}));

  if (!response.ok) {
    const message =
      typeof data.detail === "string"
        ? data.detail
        : `Request failed (${response.status})`;

    throw new Error(message);
  }

  return data as T;
}

export async function registerUser(input: {
  name: string;
  email: string;
  password: string;
}) {
  return request<{ message: string; user_id: number }>(
    "/api/auth/register",
    {
      method: "POST",
      body: JSON.stringify(input),
    },
  );
}


export async function loginUser(input: {
  email: string;
  password: string;
}) {
  const form = new URLSearchParams();
  form.set("username", input.email);
  form.set("password", input.password);

  const response = await fetch(`${API_BASE_URL}/api/auth/login`, {
    method: "POST",
    headers: {
      "Content-Type": "application/x-www-form-urlencoded",
    },
    body: form.toString(),
  });

  const data = await response.json().catch(() => ({}));

  if (!response.ok) {
    throw new Error(
      typeof data.detail === "string"
        ? data.detail
        : `Login failed (${response.status})`,
    );
  }

  return data as {
    access_token: string;
    token_type: string;
    user_id: number;
  };
}


export async function getCurrentUser(token: string) {
  return request<UserProfile>("/api/auth/me", {}, token);
}
