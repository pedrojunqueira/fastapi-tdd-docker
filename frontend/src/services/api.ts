import { apiConfig } from "../config/authConfig";
import type {
  User,
  UserUpdatePayload,
  Summary,
  SummaryCreatePayload,
  SummaryUpdatePayload,
} from "../types";

class ApiService {
  private baseUrl: string;

  constructor() {
    this.baseUrl = apiConfig.baseUrl;
  }

  private async request<T>(
    endpoint: string,
    token: string,
    options: RequestInit = {}
  ): Promise<T> {
    const url = `${this.baseUrl}${endpoint}`;

    const response = await fetch(url, {
      ...options,
      headers: {
        "Content-Type": "application/json",
        Authorization: `Bearer ${token}`,
        ...options.headers,
      },
    });

    if (!response.ok) {
      const error = await response
        .json()
        .catch(() => ({ detail: "Unknown error" }));
      throw new Error(error.detail || `HTTP error ${response.status}`);
    }

    return response.json();
  }

  // ============ User endpoints ============

  async registerUser(token: string): Promise<User> {
    return this.request<User>("/users/register", token, {
      method: "POST",
    });
  }

  async getCurrentUser(token: string): Promise<User> {
    return this.request<User>("/users/me", token);
  }

  async getUsers(token: string): Promise<User[]> {
    const response = await this.request<{ users: User[]; total: number }>(
      "/users/",
      token
    );
    return response.users;
  }

  async getUser(token: string, userId: number): Promise<User> {
    return this.request<User>(`/users/${userId}`, token);
  }

  async updateUser(
    token: string,
    userId: number,
    payload: UserUpdatePayload
  ): Promise<User> {
    return this.request<User>(`/users/${userId}`, token, {
      method: "PUT",
      body: JSON.stringify(payload),
    });
  }

  async deleteUser(token: string, userId: number): Promise<void> {
    await this.request<void>(`/users/${userId}`, token, {
      method: "DELETE",
    });
  }

  // ============ Summary endpoints ============

  async getSummaries(token: string): Promise<Summary[]> {
    return this.request<Summary[]>("/summaries/", token);
  }

  async getSummary(token: string, summaryId: number): Promise<Summary> {
    return this.request<Summary>(`/summaries/${summaryId}/`, token);
  }

  async createSummary(
    token: string,
    payload: SummaryCreatePayload
  ): Promise<Summary> {
    return this.request<Summary>("/summaries/", token, {
      method: "POST",
      body: JSON.stringify(payload),
    });
  }

  async updateSummary(
    token: string,
    summaryId: number,
    payload: SummaryUpdatePayload
  ): Promise<Summary> {
    return this.request<Summary>(`/summaries/${summaryId}/`, token, {
      method: "PUT",
      body: JSON.stringify(payload),
    });
  }

  async deleteSummary(token: string, summaryId: number): Promise<void> {
    await this.request<void>(`/summaries/${summaryId}/`, token, {
      method: "DELETE",
    });
  }
}

export const api = new ApiService();
