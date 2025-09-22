export interface User {
  id: number;
  username?: string;
  email: string;
  full_name: string;
  role: 'admin' | 'staff' | 'viewer';
  is_active: boolean;
  created_at: string;
  updated_at: string;
  last_login?: string;
}

export interface UserCreate {
  username?: string;
  email: string;
  full_name: string;
  role?: 'admin' | 'staff' | 'viewer';
  is_active?: boolean;
  password: string;
}

export interface UserUpdate {
  username?: string;
  email?: string;
  full_name?: string;
  role?: 'admin' | 'staff' | 'viewer';
  is_active?: boolean;
  password?: string;
}

export interface LoginRequest {
  username: string;
  password: string;
}

export interface LoginResponse {
  access_token: string;
  token_type: string;
  user: User;
}
