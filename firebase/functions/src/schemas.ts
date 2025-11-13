// TypeScript interfaces for the AI Task Router
export interface TaskSpec {
  user_query: string;
  source_url?: string;
  desired_style?: string;
  desired_length?: string;
}

export interface FinalPackage {
  final_output: string;
  metadata: {
    processing_time: number;
    agents_used: string[];
    word_count: number;
    style: string;
    length_category: string;
  };
}

export interface AgentResult {
  agent_name: string;
  output: string;
  confidence: number;
  processing_time: number;
}
