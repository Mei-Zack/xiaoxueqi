import { http } from '@/utils/http'

// 获取血糖数据
export function getGlucoseData(params?: {
  start_date?: string
  end_date?: string
  limit?: number
}) {
  return http.request<{
    items: Array<{
      id: number
      value: number
      measured_at: string
      measurement_time: string
      measurement_method: string
      notes?: string
    }>
    total: number
  }>({
    url: '/api/v1/glucose-monitor/device-data',
    method: 'get',
    params
  })
}

// 添加血糖记录
export function addGlucoseRecord(data: {
  value: number
  measured_at: string
  measurement_time: string
  measurement_method: string
  notes?: string
}) {
  return http.request<{
    id: number
    value: number
    measured_at: string
    measurement_time: string
    measurement_method: string
    notes?: string
  }>({
    url: '/api/v1/glucose-monitor/record',
    method: 'post',
    data
  })
}

// 同步设备数据
export function syncDeviceData(deviceType: string, params?: any) {
  return http.request<{
    success: boolean
    message: string
    data?: any[]
  }>({
    url: '/api/v1/glucose-monitor/import-device-data',
    method: 'post',
    data: {
      device_type: deviceType,
      params: params
    }
  })
} 