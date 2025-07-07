/**
 * 糖尿病助手项目统一数据模型
 * 确保前端和后端使用一致的数据结构
 */

// 用户相关模型
export interface User {
  id: string;
  email: string;
  username: string;
  full_name: string;
  is_active: boolean;
  created_at: string;
  updated_at: string;
}

export interface UserCreate {
  email: string;
  username: string;
  password: string;
  full_name?: string;
}

export interface UserLogin {
  username: string;
  password: string;
}

export interface UserUpdate {
  email?: string;
  full_name?: string;
  password?: string;
}

export interface TokenResponse {
  access_token: string;
  token_type: string;
}

// 血糖记录相关模型
export enum MeasurementTime {
  BEFORE_BREAKFAST = 'BEFORE_BREAKFAST',
  AFTER_BREAKFAST = 'AFTER_BREAKFAST',
  BEFORE_LUNCH = 'BEFORE_LUNCH',
  AFTER_LUNCH = 'AFTER_LUNCH',
  BEFORE_DINNER = 'BEFORE_DINNER',
  AFTER_DINNER = 'AFTER_DINNER',
  BEFORE_SLEEP = 'BEFORE_SLEEP',
  MIDNIGHT = 'MIDNIGHT',
  OTHER = 'OTHER'
}

export enum MeasurementMethod {
  FINGER_STICK = 'FINGER_STICK',
  CONTINUOUS_MONITOR = 'CONTINUOUS_MONITOR',
  LAB_TEST = 'LAB_TEST',
  OTHER = 'OTHER'
}

export interface GlucoseRecord {
  id: string;
  user_id: string;
  value: number;
  measured_at: string;
  measurement_time: MeasurementTime;
  measurement_method: MeasurementMethod;
  notes?: string;
  created_at: string;
  updated_at: string;
}

export interface GlucoseCreate {
  user_id: string;
  value: number;
  measured_at: string;
  measurement_time: MeasurementTime;
  measurement_method: MeasurementMethod;
  notes?: string;
}

export interface GlucoseUpdate {
  value?: number;
  measured_at?: string;
  measurement_time?: MeasurementTime;
  measurement_method?: MeasurementMethod;
  notes?: string;
}

export interface GlucoseStatistics {
  average: number;
  max_value: number;
  min_value: number;
  count: number;
  high_count: number;
  low_count: number;
  in_range_percentage: number;
  high_percentage: number;
  low_percentage: number;
  std_deviation: number;
  period: string;
}

export interface GlucoseAnalysis {
  statistics: {
    average: number;
    max: number;
    min: number;
    std: number;
    in_range_percentage: number;
    high_percentage: number;
    low_percentage: number;
  };
  patterns: Record<string, any>;
  advice: string;
  record_count: number;
  updated_at: string;
}

// 健康记录相关模型
export interface HealthRecord {
  id: string;
  user_id: string;
  weight?: number;
  blood_pressure_systolic?: number;
  blood_pressure_diastolic?: number;
  heart_rate?: number;
  temperature?: number;
  oxygen_saturation?: number;
  steps?: number;
  sleep_hours?: number;
  notes?: string;
  recorded_at: string;
  created_at: string;
  updated_at: string;
}

export interface HealthCreate {
  user_id: string;
  weight?: number;
  blood_pressure_systolic?: number;
  blood_pressure_diastolic?: number;
  heart_rate?: number;
  temperature?: number;
  oxygen_saturation?: number;
  steps?: number;
  sleep_hours?: number;
  notes?: string;
  recorded_at: string;
}

export interface HealthUpdate {
  weight?: number;
  blood_pressure_systolic?: number;
  blood_pressure_diastolic?: number;
  heart_rate?: number;
  temperature?: number;
  oxygen_saturation?: number;
  steps?: number;
  sleep_hours?: number;
  notes?: string;
  recorded_at?: string;
}

// 饮食记录相关模型
export interface DietRecord {
  id: string;
  user_id: string;
  meal_type: string;
  food_items: string[];
  carbohydrates?: number;
  proteins?: number;
  fats?: number;
  calories?: number;
  notes?: string;
  consumed_at: string;
  created_at: string;
  updated_at: string;
}

export interface DietCreate {
  user_id: string;
  meal_type: string;
  food_items: string[];
  carbohydrates?: number;
  proteins?: number;
  fats?: number;
  calories?: number;
  notes?: string;
  consumed_at: string;
}

export interface DietUpdate {
  meal_type?: string;
  food_items?: string[];
  carbohydrates?: number;
  proteins?: number;
  fats?: number;
  calories?: number;
  notes?: string;
  consumed_at?: string;
}

// 助手对话相关模型
export interface Conversation {
  id: string;
  user_id: string;
  title: string;
  created_at: string;
  updated_at: string;
}

export interface Message {
  id: string;
  conversation_id: string;
  role: 'user' | 'assistant';
  content: string;
  created_at: string;
}

export interface ConversationCreate {
  user_id: string;
  title: string;
}

export interface MessageCreate {
  conversation_id: string;
  role: 'user' | 'assistant';
  content: string;
}

// 知识库相关模型
export interface KnowledgeEntry {
  id: string;
  title: string;
  content: string;
  category: string;
  tags: string[];
  created_at: string;
  updated_at: string;
}

export interface KnowledgeCreate {
  title: string;
  content: string;
  category: string;
  tags: string[];
}

export interface KnowledgeUpdate {
  title?: string;
  content?: string;
  category?: string;
  tags?: string[];
}

// API响应通用接口
export interface ApiResponse<T> {
  data: T;
  message?: string;
  status?: string;
}

export interface PaginatedResponse<T> {
  items: T[];
  total: number;
  page: number;
  size: number;
  pages: number;
}

// 错误响应接口
export interface ValidationError {
  loc: string[];
  msg: string;
  type: string;
}

export interface ErrorResponse {
  detail: string | ValidationError[] | Record<string, any>;
} 