export interface SizeStock {
  size: string;
  quantity: number;
}

export interface Product {
  product_id: string;
  name: string;
  garment_type: string;
  description: string;
  colors: string[];
  search_tags: string[];
  image_url: string;
  price: number;
  inventory: SizeStock[];
  total_stock: number;
}

export interface PublicUser {
  id: number;
  first_name?: string | null;
  last_name?: string | null;
  name: string;
  email: string;
}

export interface AuthResponse {
  token: string;
  user: PublicUser;
}

export interface ChatMessage {
  role: "user" | "assistant";
  content: string;
}

export interface ChatResponse {
  reply: string;
  products: Product[];
}

export interface ChatHistoryTurn {
  role: "user" | "assistant";
  content: string;
  products: Product[];
}

export interface CartItem {
  product_id: string;
  name: string;
  price: number;
  image_url: string;
  size: string;
  quantity: number;
}
