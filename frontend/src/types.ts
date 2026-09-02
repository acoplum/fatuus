export interface SlopMatch {
  term: string;
  start: number;
  end: number;
  pattern: string;
}

export interface SentenceMetrics {
  sentence_count: number;
  avg_words_per_sentence: number;
  std_dev_words: number;
  burstiness: number;
}

export interface InvisibleChar {
  char_code: string;
  name: string;
  position: number;
}

export interface ProbeResult {
  word_count: number;
  synthetic_score: number;
  slop_count: number;
  slop_density_per_100_words: number;
  invisible_char_count: number;
  sentence_metrics: SentenceMetrics;
  slop_matches: SlopMatch[];
  invisible_chars: InvisibleChar[];
}

export interface Layer0Result {
  cleaned_text: string;
  invisible_removed: number;
  slop_replaced: number;
}

export interface CleanResult {
  cleaned_text: string;
  layer0: Layer0Result;
  layer1_accepted: boolean;
  layer1_attempts: number;
  gate_reasons: string[];
}

export interface AnalysisReport {
  originalText: string;
  clean: CleanResult;
  before: ProbeResult;
  after: ProbeResult;
}
