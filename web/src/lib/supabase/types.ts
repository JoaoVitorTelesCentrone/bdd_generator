export type Json =
  | string
  | number
  | boolean
  | null
  | { [key: string]: Json | undefined }
  | Json[];

export interface Database {
  public: {
    Tables: {
      profiles: {
        Row: {
          id: string;
          email: string;
          full_name: string | null;
          avatar_url: string | null;
          created_at: string;
        };
        Insert: {
          id: string;
          email: string;
          full_name?: string | null;
          avatar_url?: string | null;
          created_at?: string;
        };
        Update: {
          email?: string;
          full_name?: string | null;
          avatar_url?: string | null;
        };
      };
      generations: {
        Row: {
          id: string;
          user_id: string;
          story: string;
          model: string;
          bdd_text: string;
          score_final: number;
          cobertura: number;
          clareza: number;
          estrutura: number;
          executabilidade: number;
          aprovado: boolean;
          attempts: number;
          total_tokens: number;
          research_tokens: number;
          duration_seconds: number;
          converged: boolean;
          research_enabled: boolean;
          threshold: number;
          created_at: string;
        };
        Insert: {
          id?: string;
          user_id: string;
          story: string;
          model: string;
          bdd_text: string;
          score_final: number;
          cobertura: number;
          clareza: number;
          estrutura: number;
          executabilidade: number;
          aprovado: boolean;
          attempts: number;
          total_tokens: number;
          research_tokens?: number;
          duration_seconds: number;
          converged: boolean;
          research_enabled?: boolean;
          threshold?: number;
          created_at?: string;
        };
        Update: Partial<Database["public"]["Tables"]["generations"]["Insert"]>;
      };
    };
    Views: Record<string, never>;
    Functions: Record<string, never>;
    Enums: Record<string, never>;
  };
}

// Aliases para uso mais fácil
export type Profile    = Database["public"]["Tables"]["profiles"]["Row"];
export type Generation = Database["public"]["Tables"]["generations"]["Row"];
export type GenerationInsert = Database["public"]["Tables"]["generations"]["Insert"];
