import { http } from '../utils/http'
import type { 
  GlucoseRecord, 
  GlucoseCreate, 
  GlucoseUpdate, 
  GlucoseStatistics, 
  PaginatedResponse 
} from '../types/models'

const BASE_URL = '/api/v1/glucose'

/**
 * 血糖记录API服务
 */
export const glucoseApi = {
  /**
   * 获取血糖记录列表
   * @param params 查询参数
   * @returns 血糖记录列表
   */
  getGlucoseRecords: (params?: { 
    page?: number; 
    size?: number; 
    start_date?: string; 
    end_date?: string 
  }) => {
    return http.get<PaginatedResponse<GlucoseRecord>>(BASE_URL, { params })
  },

  /**
   * 获取单个血糖记录
   * @param id 血糖记录ID
   * @returns 血糖记录详情
   */
  getGlucoseRecord: (id: string) => {
    return http.get<GlucoseRecord>(`${BASE_URL}/${id}`)
  },

  /**
   * 添加血糖记录
   * @param data 血糖记录数据
   * @returns 创建的血糖记录
   */
  addGlucoseRecord: (data: GlucoseCreate) => {
    return http.post<GlucoseRecord>(BASE_URL, data)
  },

  /**
   * 更新血糖记录
   * @param id 血糖记录ID
   * @param data 更新的数据
   * @returns 更新后的血糖记录
   */
  updateGlucoseRecord: (id: string, data: GlucoseUpdate) => {
    return http.put<GlucoseRecord>(`${BASE_URL}/${id}`, data)
  },

  /**
   * 删除血糖记录
   * @param id 血糖记录ID
   * @returns 操作结果
   */
  deleteGlucoseRecord: (id: string) => {
    return http.delete(`${BASE_URL}/${id}`)
  },

  /**
   * 获取血糖统计数据
   * @param params 查询参数
   * @returns 血糖统计数据
   */
  getGlucoseStatistics: (params?: { 
    period?: 'day' | 'week' | 'month' | 'year'; 
    start_date?: string; 
    end_date?: string 
  }) => {
    return http.get<GlucoseStatistics>(`${BASE_URL}/statistics`, { params })
  },

  /**
   * 获取最近血糖记录
   * @param params 查询参数
   * @returns 最近的血糖记录列表
   */
  getRecentGlucoseRecords: (params?: { days?: number }) => {
    return http.get<GlucoseRecord[]>(`${BASE_URL}/recent`, { params })
  }
}

export default glucoseApi 