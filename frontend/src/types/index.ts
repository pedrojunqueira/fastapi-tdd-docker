// Type definitions for the application

// User types
export interface User {
  id: number;
  email: string;
  role: "admin" | "writer" | "reader";
  created_at?: string;
  last_login?: string;
}

export interface UserUpdatePayload {
  role: "admin" | "writer" | "reader";
}

export interface UserListResponse {
  users: User[];
  total: number;
}

// Summary types
export interface Summary {
  id: number;
  url: string;
  summary: string;
  user_id: number;
  created_at: string;
}

export interface SummaryCreatePayload {
  url: string;
  summary?: string;
}

export interface SummaryUpdatePayload {
  url: string;
  summary: string;
}

// API Response types
export interface ApiError {
  detail: string;
}

// Auth context types
export interface AuthContextType {
  isAuthenticated: boolean;
  isLoading: boolean;
  user: User | null;
  accessToken: string | null;
  login: () => Promise<void>;
  logout: () => void;
  registerUser: () => Promise<User | null>;
  refreshUser: () => Promise<void>;
}
