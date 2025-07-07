import { ElMessage, ElMessageBox } from 'element-plus'
import { http } from './http'
import type { AxiosRequestConfig } from 'axios'
import type { ApiResponse, PaginatedResponse } from '../types/models'

/**
 * API辅助工具类
 * 提供统一的API调用方法，包括错误处理和数据格式化
 */
export class ApiHelper {
  /**
   * 执行API请求并处理错误
   * @param apiCall API调用函数
   * @param errorMessage 错误消息
   * @param showSuccessMessage 是否显示成功消息
   * @param successMessage 成功消息
   * @returns 请求结果
   */
  static async execute<T>(
    apiCall: () => Promise<T>,
    errorMessage: string = '操作失败',
    showSuccessMessage: boolean = false,
    successMessage: string = '操作成功'
  ): Promise<T | null> {
    try {
      const result = await apiCall()
      
      if (showSuccessMessage) {
        ElMessage.success(successMessage)
      }
      
      return result
    } catch (error) {
      console.error(`API错误: ${errorMessage}`, error)
      
      // 错误处理已经在http拦截器中完成，这里不需要再显示错误消息
      return null
    }
  }
  
  /**
   * 执行需要确认的API请求
   * @param apiCall API调用函数
   * @param confirmMessage 确认消息
   * @param confirmTitle 确认标题
   * @param errorMessage 错误消息
   * @param successMessage 成功消息
   * @returns 请求结果
   */
  static async executeWithConfirm<T>(
    apiCall: () => Promise<T>,
    confirmMessage: string = '确定要执行此操作吗？',
    confirmTitle: string = '确认',
    errorMessage: string = '操作失败',
    successMessage: string = '操作成功'
  ): Promise<T | null> {
    try {
      await ElMessageBox.confirm(
        confirmMessage,
        confirmTitle,
        {
          confirmButtonText: '确定',
          cancelButtonText: '取消',
          type: 'warning'
        }
      )
      
      const result = await apiCall()
      ElMessage.success(successMessage)
      return result
    } catch (error: any) {
      if (error === 'cancel') {
        return null
      }
      
      console.error(`API错误: ${errorMessage}`, error)
      return null
    }
  }
  
  /**
   * 获取分页数据
   * @param url API路径
   * @param params 查询参数
   * @param config Axios配置
   * @returns 分页数据
   */
  static async getPaginatedData<T>(
    url: string,
    params: Record<string, any> = {},
    config?: AxiosRequestConfig
  ): Promise<PaginatedResponse<T> | null> {
    return this.execute<PaginatedResponse<T>>(
      () => http.get<PaginatedResponse<T>>(url, { ...config, params }),
      '获取数据失败'
    )
  }
  
  /**
   * 获取单个资源
   * @param url API路径
   * @param config Axios配置
   * @returns 资源数据
   */
  static async getResource<T>(
    url: string,
    config?: AxiosRequestConfig
  ): Promise<T | null> {
    return this.execute<T>(
      () => http.get<T>(url, config),
      '获取数据失败'
    )
  }
  
  /**
   * 创建资源
   * @param url API路径
   * @param data 请求数据
   * @param config Axios配置
   * @param showSuccessMessage 是否显示成功消息
   * @returns 创建的资源
   */
  static async createResource<T>(
    url: string,
    data: any,
    config?: AxiosRequestConfig,
    showSuccessMessage: boolean = true
  ): Promise<T | null> {
    return this.execute<T>(
      () => http.post<T>(url, data, config),
      '创建失败',
      showSuccessMessage,
      '创建成功'
    )
  }
  
  /**
   * 更新资源
   * @param url API路径
   * @param data 请求数据
   * @param config Axios配置
   * @param showSuccessMessage 是否显示成功消息
   * @returns 更新的资源
   */
  static async updateResource<T>(
    url: string,
    data: any,
    config?: AxiosRequestConfig,
    showSuccessMessage: boolean = true
  ): Promise<T | null> {
    return this.execute<T>(
      () => http.put<T>(url, data, config),
      '更新失败',
      showSuccessMessage,
      '更新成功'
    )
  }
  
  /**
   * 删除资源
   * @param url API路径
   * @param config Axios配置
   * @returns 删除结果
   */
  static async deleteResource<T = any>(
    url: string,
    config?: AxiosRequestConfig
  ): Promise<T | null> {
    return this.executeWithConfirm<T>(
      () => http.delete<T>(url, config),
      '确定要删除此项吗？此操作不可撤销。',
      '删除确认',
      '删除失败',
      '删除成功'
    )
  }
  
  /**
   * 格式化日期时间
   * @param dateString ISO日期字符串
   * @param format 格式化选项
   * @returns 格式化后的日期时间字符串
   */
  static formatDateTime(dateString: string, format: 'date' | 'time' | 'datetime' = 'datetime'): string {
    if (!dateString) return ''
    
    try {
      const date = new Date(dateString)
      
      switch (format) {
        case 'date':
          return date.toLocaleDateString('zh-CN')
        case 'time':
          return date.toLocaleTimeString('zh-CN')
        case 'datetime':
        default:
          return date.toLocaleString('zh-CN')
      }
    } catch (error) {
      console.error('日期格式化错误:', error)
      return dateString
    }
  }
  
  /**
   * 格式化血糖测量类型
   * @param measurementTime 测量类型编码
   * @returns 格式化后的测量类型文本
   */
  static formatMeasurementTime(measurementTime: string): string {
    const map: Record<string, string> = {
      'BEFORE_BREAKFAST': '早餐前',
      'AFTER_BREAKFAST': '早餐后',
      'BEFORE_LUNCH': '午餐前',
      'AFTER_LUNCH': '午餐后',
      'BEFORE_DINNER': '晚餐前',
      'AFTER_DINNER': '晚餐后',
      'BEFORE_SLEEP': '睡前',
      'MIDNIGHT': '半夜',
      'OTHER': '其他'
    }
    
    return map[measurementTime] || measurementTime
  }
  
  /**
   * 格式化血糖测量方法
   * @param measurementMethod 测量方法编码
   * @returns 格式化后的测量方法文本
   */
  static formatMeasurementMethod(measurementMethod: string): string {
    const map: Record<string, string> = {
      'FINGER_STICK': '指尖采血',
      'CONTINUOUS_MONITOR': '连续监测',
      'LAB_TEST': '实验室检验',
      'OTHER': '其他'
    }
    
    return map[measurementMethod] || measurementMethod
  }
}

export default ApiHelper 