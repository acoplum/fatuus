export interface SlopMatch {
  term: string;
  start: number;
  end: number;
  pattern: string;
}

export interface StructuralMatch extends SlopMatch {
  name: string;
}

export interface TypographyMetrics {
  em_dash_count: number;
  em_dash_per_100_words: number;
  curly_quote_count: number;
  ellipsis_char_count: number;
  space_lookalike_count: number;
}

export interface FormattingMetrics {
  bold_segment_count: number;
  bold_bullet_count: number;
  emoji_heading_count: number;
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
  structural_count: number;
  sentence_metrics: SentenceMetrics;
  typography: TypographyMetrics;
  formatting: FormattingMetrics;
  slop_matches: SlopMatch[];
  structural_matches: StructuralMatch[];
  invisible_chars: InvisibleChar[];
}

export interface Layer0Result {
  cleaned_text: string;
  invisible_removed: number;
  typography_normalized: number;
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
