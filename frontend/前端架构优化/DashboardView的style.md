</script>

<style scoped>
@keyframes fadeInUp {
  from {
    opacity: 0;
    transform: translateY(20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

/* 定义主题色变量 */
:root {
  --metric-color: #2ecc71; /* 绿色 */
  --diet-suggestion-color: #e67e22; /* 橙色 */
  --diet-record-color: #f1c40f; /* 黄色 */
  --glucose-monitor-color: #3498db; /* 蓝色 */
  --reminder-color: #9b59b6; /* 紫色 */
  --knowledge-color: #34495e; /* 深蓝灰色 */
}

.dashboard-container {
  padding: 24px;
  background-color: #f0f4f8;
  font-family: 'Helvetica Neue', Helvetica, 'PingFang SC', 'Hiragino Sans GB', 'Microsoft YaHei', '微软雅黑', Arial, sans-serif;
}

.el-card {
  margin-bottom: 24px;
  border-radius: 16px;
  border: none;
  box-shadow: 0 8px 16px rgba(0, 0, 0, 0.05);
  transition: all 0.3s ease;
  overflow: hidden; /* 配合圆角 */
  animation: fadeInUp 0.5s ease-in-out forwards;
  opacity: 0; /* 初始状态为透明 */
}

/* 为不同的卡片添加动画延迟，实现错落效果 */
.el-row > .el-col:nth-child(1) .el-card { animation-delay: 0.1s; }
.el-row > .el-col:nth-child(2) .el-card { animation-delay: 0.2s; }
.el-row > .el-col:nth-child(3) .el-card { animation-delay: 0.3s; }
.el-row .el-col .el-row > .el-col:nth-child(1) .el-card { animation-delay: 0.2s; }
.el-row .el-col .el-row > .el-col:nth-child(2) .el-card { animation-delay: 0.3s; }
.el-row .el-col .el-row > .el-col:nth-child(3) .el-card { animation-delay: 0.4s; }

.el-card:hover {
  transform: translateY(-5px) scale(1.03);
  box-shadow: 0 12px 24px rgba(0, 0, 0, 0.08);
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-weight: 600;
  font-size: 1.1rem;
  color: #2c3e50;
  border-bottom: 1px solid #eef2f7;
  padding-bottom: 10px;
}

/* 为特定卡片添加彩色左边框 */
.metric-card { border-left: 5px solid var(--metric-color); }
.diet-suggestion-card { border-left: 5px solid var(--diet-suggestion-color); }
.diet-card { border-left: 5px solid var(--diet-record-color); }
.glucose-card { border-left: 5px solid var(--glucose-monitor-color); }
.reminder-card { border-left: 5px solid var(--reminder-color); }
.knowledge-card { border-left: 5px solid var(--knowledge-color); }

/* 为卡片头部的文字或图标应用主题色 */
.metric-card .card-header span { color: var(--metric-color); }
.diet-suggestion-card .card-header span { color: var(--diet-suggestion-color); }
.diet-card .card-header span { color: var(--diet-record-color); }
.glucose-card .card-header span { color: var(--glucose-monitor-color); }
.reminder-card .card-header span { color: var(--reminder-color); }
.knowledge-card .card-header span { color: var(--knowledge-color); }

.welcome-card {
  background: linear-gradient(135deg, #00c6ff, #0072ff);
  color: white;
}

.welcome-content {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 10px;
}

.welcome-text h2 {
  margin: 0;
  font-size: 2rem;
  font-weight: 700;
}

.welcome-text p {
  margin: 8px 0 0;
  opacity: 0.9;
  font-size: 1rem;
}

.welcome-actions {
  display: flex;
  gap: 15px;
}

.welcome-actions .el-button--primary {
  background-color: #ffffff !important;
  color: #0072ff;
  border: none;
  border-radius: 20px;
  font-weight: 600;
  box-shadow: 0 4px 10px rgba(0, 0, 0, 0.1);
}

.welcome-actions .el-button {
  background-color: rgba(255, 255, 255, 0.2) !important;
  color: #ffffff;
  border: 1px solid rgba(255, 255, 255, 0.8);
  border-radius: 20px;
  font-weight: 600;
}

.chart-card .card-header {
  border-bottom: none;
}

.chart-container {
  height: 350px;
  width: 100%;
  margin: 0;
  border: none;
  border-radius: 4px;
}

.chart {
  width: 100%;
  height: 100%;
  min-height: 350px;
}

.metrics-container {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 20px;
}

.metric-item {
  text-align: center;
  padding: 16px;
  background-color: #f8f9fa;
  border-radius: 12px;
}

.metric-label {
  color: #576b81;
  font-size: 0.9rem;
  margin-bottom: 8px;
}

.metric-value {
  font-size: 1.6rem;
  font-weight: 700;
  color: var(--metric-color);
}

.diet-card .diet-list {
  padding: 0 10px;
}

.diet-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px 0;
  border-bottom: 1px solid #eef2f7;
}

.diet-item:last-child {
  border-bottom: none;
}

.diet-time {
  font-size: 0.9rem;
  color: #576b81;
  width: 30%;
  font-weight: 500;
}

.diet-name {
  flex: 1;
  font-weight: 500;
}

.diet-calories {
  color: var(--diet-record-color);
  font-weight: 600;
}

.reminder-list {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.reminder-item {
  display: flex;
  align-items: center;
  padding: 12px;
  background-color: #f8f9fa;
  border-radius: 10px;
  transition: background-color 0.3s;
}

.reminder-icon {
  margin-right: 12px;
  font-size: 1.4rem;
  color: var(--reminder-color);
}

.reminder-icon.done {
  color: #2ecc71;
}

.reminder-content {
  flex: 1;
}

.reminder-text {
  font-weight: 600;
  color: #2c3e50;
}

.reminder-time {
  font-size: 0.8rem;
  color: #576b81;
}

.reminder-item .el-checkbox {
  margin-left: 10px;
}

.knowledge-item {
  padding: 16px 0;
  border-bottom: 1px solid #eef2f7;
}

.knowledge-item:last-child {
  border-bottom: none;
}

.knowledge-title {
  font-weight: 600;
  margin-bottom: 6px;
  color: #2c3e50;
}

.knowledge-desc {
  font-size: 0.9rem;
  color: #576b81;
  margin-bottom: 12px;
}

.knowledge-item .el-button {
  font-weight: 600;
}

.card-footer {
  margin-top: 16px;
  text-align: center;
}

.empty-data {
  padding: 40px 0;
}

.loading-container {
  padding: 20px;
}

.glucose-card .card-header {
  border-bottom: none;
}

.quick-import {
  padding: 10px 5px;
}

.quick-import h4 {
  margin-bottom: 15px;
  color: var(--glucose-monitor-color);
  font-weight: 600;
}

.quick-import .el-button {
  border-radius: 8px;
  font-weight: 600;
}

.glucose-alerts {
  margin-bottom: 15px;
}

.glucose-alerts .el-alert {
  margin-bottom: 10px;
  border-radius: 8px;
}

.glucose-alerts .el-alert:last-child {
  margin-bottom: 0;
}

/* 智能分析相关样式 */
.glucose-analysis {
  margin-top: 10px;
}

.analysis-summary {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 10px;
  margin-bottom: 15px;
}

.summary-item {
  text-align: center;
  flex: 1;
  padding: 12px 0;
  border-radius: 12px;
}

.summary-value {
  font-size: 20px;
  font-weight: 700;
  margin-bottom: 4px;
}

.summary-label {
  font-size: 13px;
  font-weight: 500;
}

.normal-value { background-color: rgba(46, 204, 113, 0.1); color: #2ecc71; }
.high-value { background-color: rgba(231, 76, 60, 0.1); color: #e74c3c; }
.low-value { background-color: rgba(243, 156, 18, 0.1); color: #f39c12; }

.good-range { background-color: rgba(46, 204, 113, 0.1); color: #2ecc71; }
.average-range { background-color: rgba(243, 156, 18, 0.1); color: #f39c12; }
.poor-range { background-color: rgba(231, 76, 60, 0.1); color: #e74c3c; }

.stable-std { background-color: rgba(46, 204, 113, 0.1); color: #2ecc71; }
.moderate-std { background-color: rgba(243, 156, 18, 0.1); color: #f39c12; }
.unstable-std { background-color: rgba(231, 76, 60, 0.1); color: #e74c3c; }

.advice-preview {
  background-color: #eaf5ff;
  border-radius: 12px;
  padding: 16px;
  margin-bottom: 10px;
  border: 1px solid #a8d8ff;
}

.advice-title {
  display: flex;
  align-items: center;
  margin-bottom: 8px;
  color: var(--glucose-monitor-color);
  font-weight: 600;
}

.advice-title .el-icon {
  margin-right: 8px;
  font-size: 1.2rem;
}

.advice-content {
  font-size: 14px;
  line-height: 1.6;
  color: #34495e;
  margin-bottom: 8px;
}

.empty-analysis {
  padding: 15px 0;
  text-align: center;
}

/* 对话框样式 */
:deep(.advice-dialog .el-message-box__content) {
  max-height: 400px;
  overflow-y: auto;
}

.diet-suggestion-card .card-header {
  border-bottom: none;
}

.diet-status-banner {
  display: flex;
  align-items: center;
  padding: 12px;
  border-radius: 10px;
  margin-bottom: 15px;
  font-size: 14px;
  font-weight: 600;
}

.diet-status-banner .el-icon {
  margin-right: 8px;
  font-size: 18px;
}

.status-normal {
  background-color: rgba(46, 204, 113, 0.15);
  color: #27ae60;
  border-left: 5px solid #2ecc71;
}

.status-high {
  background-color: rgba(231, 76, 60, 0.15);
  color: #c0392b;
  border-left: 5px solid #e74c3c;
}

.status-low {
  background-color: rgba(243, 156, 18, 0.15);
  color: #d35400;
  border-left: 5px solid #f39c12;
}

.diet-suggestion-content {
  padding: 0 5px;
}

.suggestion-text {
  font-size: 14px;
  line-height: 1.6;
  margin-bottom: 20px;
  color: #34495e;
}

.food-section {
  margin-bottom: 20px;
}

.food-section h4 {
  font-size: 15px;
  margin-bottom: 10px;
  color: #2c3e50;
  font-weight: 600;
}

.food-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
}

.food-tag {
  border-radius: 16px;
  padding: 0 15px;
  height: 32px;
  line-height: 30px;
  font-weight: 500;
}

.next-meal {
  margin: 20px 0;
}

.meal-type-selector {
  margin-bottom: 15px;
  text-align: center;
}

.meal-suggestion {
  background-color: #f0f4f8;
  padding: 15px;
  border-radius: 10px;
  font-size: 14px;
  line-height: 1.6;
  color: #34495e;
  text-align: center;
  border: 1px dashed #bdc3c7;
}

.card-footer {
  margin-top: 20px;
  text-align: center;
}

:deep(.diet-suggestion-dialog .el-message-box__content) {
  max-height: 400px;
  overflow-y: auto;
}

:deep(.diet-suggestion-dialog ul) {
  padding-left: 20px;
  margin: 10px 0;
  list-style-type: "✨ ";
}

:deep(.diet-suggestion-dialog h3, .diet-suggestion-dialog h4) {
  margin: 15px 0 10px 0;
  color: #0072ff;
}

:deep(.diet-suggestion-dialog .blood-glucose-analysis) {
  margin-bottom: 20px;
  padding: 15px;
  background-color: #f8f9fb;
  border-radius: 8px;
  border-left: 4px solid #409EFF;
}

:deep(.diet-suggestion-dialog .additional-meal-suggestions) {
  margin-top: 25px;
  padding-top: 15px;
  border-top: 1px dashed #dcdfe6;
}

:deep(.diet-suggestion-dialog strong) {
  color: #303133;
}

@media (max-width: 992px) {
  .metrics-container {
    grid-template-columns: repeat(2, 1fr);
  }
}

@media (max-width: 768px) {
  .dashboard-container {
    padding: 15px;
  }
  .welcome-content {
    flex-direction: column;
    gap: 20px;
    text-align: center;
  }
  
  .metrics-container, .analysis-summary {
    grid-template-columns: 1fr 1fr;
  }
}

@media (max-width: 576px) {
  .metrics-container, .analysis-summary {
    grid-template-columns: 1fr;
  }
  .welcome-text h2 {
    font-size: 1.8rem;
  }
  .welcome-actions {
    flex-direction: column;
    width: 100%;
  }
}

/* 添加AI血糖风险评估容器样式 */
.ai-alert-container {
  border-radius: 12px;
  padding: 16px;
  margin-bottom: 15px;
  border: 1px solid;
  box-shadow: 0 2px 6px rgba(0, 0, 0, 0.05);
  transition: all 0.3s ease-in-out;
}

.ai-alert-good {
  background-color: #f0f9eb;
  border-color: #e1f3d8;
}

.ai-alert-warning {
  background-color: #fdf6ec;
  border-color: #faecd8;
}

.ai-alert-danger {
  background-color: #fff6f6;
  border-color: #ffd6d6;
}

.ai-alert-header {
  display: flex;
  align-items: center;
  margin-bottom: 8px;
  font-weight: 600;
}

.ai-alert-good .ai-alert-header { color: #67c23a; }
.ai-alert-warning .ai-alert-header { color: #e6a23c; }
.ai-alert-danger .ai-alert-header { color: #f56c6c; }

.ai-alert-header .el-icon {
  margin-right: 8px;
  font-size: 1.2rem;
}

.ai-alert-content {
  font-size: 14px;
  line-height: 1.6;
  color: #34495e;
  margin-bottom: 8px;
  padding: 8px;
  background-color: #fff;
  border-radius: 8px;
  border-left: 3px solid;
}

.ai-alert-good .ai-alert-content { border-left-color: #67c23a; }
.ai-alert-warning .ai-alert-content { border-left-color: #e6a23c; }
.ai-alert-danger .ai-alert-content { border-left-color: #f56c6c; }

/* 对话框中AI分析内容的样式 */
:deep(.advice-dialog .ai-analysis-content) {
  line-height: 1.6;
  font-size: 14px;
}

:deep(.advice-dialog .ai-analysis-content h3) {
  color: #e74c3c;
  margin: 16px 0 8px 0;
  font-size: 16px;
  border-bottom: 1px solid #eee;
  padding-bottom: 6px;
}

:deep(.advice-dialog .ai-analysis-content h4) {
  color: #2c3e50;
  margin: 14px 0 8px 0;
  font-size: 15px;
}

:deep(.advice-dialog .ai-analysis-content strong) {
  color: #e74c3c;
  font-weight: 600;
}

:deep(.advice-dialog .el-message-box__content) {
  max-height: 60vh;
  overflow-y: auto;
  padding: 20px;
}

:deep(.advice-dialog .el-message-box__header) {
  background-color: #f8f9fb;
  padding: 15px 20px;
  border-bottom: 1px solid #eee;
}

/* 新增：血糖预警消息样式 */
:deep(.glucose-alert-warning) {
  background-color: #fff6f6;
  border: 1px solid #ffd6d6;
  border-radius: 8px;
  padding: 15px;
  margin-bottom: 20px;
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.1);
}

:deep(.glucose-alert-warning h3) {
  color: #e74c3c;
  margin-top: 0;
  margin-bottom: 10px;
  font-size: 16px;
  display: flex;
  align-items: center;
}

:deep(.glucose-alert-warning p) {
  color: #333;
  line-height: 1.6;
  margin: 0;
  font-size: 14px;
}

/* 详细建议卡片的动画延迟 */
.detailed-advice-card {
  animation-delay: 0s;
}

.el-card:hover {
  transform: translateY(-5px) scale(1.03);
  box-shadow: 0 12px 24px rgba(0, 0, 0, 0.08);
  border-left: 5px solid var(--knowledge-color);
}

.advice-content-wrapper {
  max-height: 400px;
  overflow-y: auto;
  padding-right: 15px; /* for scrollbar */
}

.advice-content-wrapper h3, .advice-content-wrapper h4 {
  margin: 15px 0 10px 0;
  color: #0072ff;
}
.advice-content-wrapper .blood-glucose-analysis {
  margin-bottom: 20px;
  padding: 15px;
  background-color: #f8f9fb;
  border-radius: 8px;
  border-left: 4px solid #409EFF;
}
.advice-content-wrapper .additional-meal-suggestions {
  margin-top: 25px;
  padding-top: 15px;
  border-top: 1px dashed #dcdfe6;
}
.advice-content-wrapper strong {
  color: #303133;
}
.advice-content-wrapper ul {
  padding-left: 20px;
  margin: 10px 0;
  list-style-type: "✨ ";
}

/* 模态框样式 */
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  width: 100vw;
  height: 100vh;
  background-color: rgba(0, 0, 0, 0.6);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 2000;
}

.modal-card {
  width: 90%;
  max-width: 800px;
  margin: 0;
  opacity: 0;
  transform: scale(0.9);
  animation: modal-pop-in 0.3s cubic-bezier(0.175, 0.885, 0.32, 1.275) forwards;
}

@keyframes modal-pop-in {
  to {
    opacity: 1;
    transform: scale(1);
  }
}

/* 新增：完整分析卡片的样式 */
.full-analysis-card {
}

.el-card:hover {
  transform: translateY(-5px) scale(1.03);
  box-shadow: 0 12px 24px rgba(0, 0, 0, 0.08);
  border-left: 5px solid var(--knowledge-color);
}

.advice-content-wrapper {
  max-height: 60vh;
  overflow-y: auto;
  padding: 20px;
}

.advice-content-wrapper h3, .advice-content-wrapper h4 {
  margin: 15px 0 10px 0;
  color: #0072ff;
}

.advice-content-wrapper .blood-glucose-analysis {
  margin-bottom: 20px;
  padding: 15px;
  background-color: #f8f9fb;
  border-radius: 8px;
  border-left: 4px solid #409EFF;
}

.advice-content-wrapper .additional-meal-suggestions {
  margin-top: 25px;
  padding-top: 15px;
  border-top: 1px dashed #dcdfe6;
}

.advice-content-wrapper strong {
  color: #303133;
}

.advice-content-wrapper ul {
  padding-left: 20px;
  margin: 10px 0;
  list-style-type: "✨ ";
}

/* 模态卡片头部的通用样式 */
.modal-card .card-header {
  background-color: #f8f9fb;
  padding: 15px 20px;
  border-bottom: 1px solid #eee;
}

/* 新增欢迎卡片加载器样式 */
.welcome-loader-container {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 160px; /* 确保加载器有足够的空间显示 */
}

.loader {
  position: relative;
  width: 240px;
  height: 130px;
  margin-bottom: 10px;
  border: 1px solid #d3d3d3;
  padding: 15px;
  background-color: #e3e3e3;
  overflow: hidden;
}

.loader:after {
  content: "";
  position: absolute;
  width: 100%;
  height: 100%;
  top: 0;
  left: 0;
  background: linear-gradient(110deg, rgba(227, 227, 227, 0) 0%, rgba(227, 227, 227, 0) 40%, rgba(227, 227, 227, 0.5) 50%, rgba(227, 227, 227, 0) 60%, rgba(227, 227, 227, 0) 100%);
  animation: gradient-animation_2 1.2s linear infinite;
}

.loader .wrapper {
  width: 100%;
  height: 100%;
  position: relative;
}

.loader .wrapper > div {
  background-color: #cacaca;
}

.loader .circle {
  width: 50px;
  height: 50px;
  border-radius: 50%;
}

.loader .button {
  display: inline-block;
  height: 32px;
  width: 75px;
}

.loader .line-1 {
  position: absolute;
  top: 11px;
  left: 58px;
  height: 10px;
  width: 100px;
}

.loader .line-2 {
  position: absolute;
  top: 34px;
  left: 58px;
  height: 10px;
  width: 150px;
}

.loader .line-3 {
  position: absolute;
  top: 57px;
  left: 0px;
  height: 10px;
  width: 100%;
}

.loader .line-4 {
  position: absolute;
  top: 80px;
  left: 0px;
  height: 10px;
  width: 92%;
}

@keyframes gradient-animation_2 {
  0% {
    transform: translateX(-100%);
  }

  100% {
    transform: translateX(100%);
  }
}

.diet-loader-container {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 200px; /* Ensure enough space for the animation */
}

/* Pizza animation CSS from uiverse.io/AkshatDaxini/jolly-hound-16 */
.main {
  width: 100%;
  height: 100%;
  display: flex;
  justify-content: center;
  align-items: center;
  position: relative;
  overflow: hidden;
  border-radius: 12px; /* Match card border-radius */
}

#pizza {
  animation: rotate 4s linear infinite; /* Rotate the entire pizza */
  transform-origin: 82px 79.5px; /* Center of the pizza */
}

#slice6 {
  animation: slice6 2s ease-in-out infinite alternate;
  transform-origin: 82px 79.5px;
}
#slice5 {
  animation: slice5 2s ease-in-out infinite alternate;
  transform-origin: 82px 79.5px;
}
#slice4 {
  animation: slice4 2s ease-in-out infinite alternate;
  transform-origin: 82px 79.5px;
}
#slice3 {
  animation: slice3 2s ease-in-out infinite alternate;
  transform-origin: 82px 79.5px;
}
#slice2 {
  animation: slice2 2s ease-in-out infinite alternate;
  transform-origin: 82px 79.5px;
}
#slice1 {
  animation: slice1 2s ease-in-out infinite alternate;
  transform-origin: 82px 79.5px;
}

#pepperoni {
  animation: pepperoni 2s ease-in-out infinite alternate;
  transform-origin: center center;
}
#pepperoni_2 {
  animation: pepperoni_2 2s ease-in-out infinite alternate;
  transform-origin: center center;
}
#pepperoni_3 {
  animation: pepperoni_3 2s ease-in-out infinite alternate;
  transform-origin: center center;
}
#pepperoni_4 {
  animation: pepperoni_4 2s ease-in-out infinite alternate;
  transform-origin: center center;
}
#pepperoni_5 {
  animation: pepperoni_5 2s ease-in-out infinite alternate;
  transform-origin: center center;
}
#pepperoni_6 {
  animation: pepperoni_6 2s ease-in-out infinite alternate;
  transform-origin: center center;
}

#mushroom {
  animation: mushroom 2s ease-in-out infinite alternate;
  transform-origin: center center;
}
#mushroom_2 {
  animation: mushroom_2 2s ease-in-out infinite alternate;
  transform-origin: center center;
}
#mushroom_3 {
  animation: mushroom_3 2s ease-in-out infinite alternate;
  transform-origin: center center;
}
#mushroom_4 {
  animation: mushroom_4 2s ease-in-out infinite alternate;
  transform-origin: center center;
}
#mushroom_5 {
  animation: mushroom_5 2s ease-in-out infinite alternate;
  transform-origin: center center;
}

#onion {
  animation: onion 2s ease-in-out infinite alternate;
  transform-origin: center center;
}
#onion_2 {
  animation: onion_2 2s ease-in-out infinite alternate;
  transform-origin: center center;
}
#onion_3 {
  animation: onion_3 2s ease-in-out infinite alternate;
  transform-origin: center center;
}
#onion_4 {
  animation: onion_4 2s ease-in-out infinite alternate;
  transform-origin: center center;
}
#onion_5 {
  animation: onion_5 2s ease-in-out infinite alternate;
  transform-origin: center center;
}
#onion_6 {
  animation: onion_6 2s ease-in-out infinite alternate;
  transform-origin: center center;
}

#pepper {
  animation: pepper 2s ease-in-out infinite alternate;
  transform-origin: center center;
}
#pepper_2 {
  animation: pepper_2 2s ease-in-out infinite alternate;
  transform-origin: center center;
}
#pepper_3 {
  animation: pepper_3 2s ease-in-out infinite alternate;
  transform-origin: center center;
}
#pepper_4 {
  animation: pepper_4 2s ease-in-out infinite alternate;
  transform-origin: center center;
}
#pepper_5 {
  animation: pepper_5 2s ease-in-out infinite alternate;
  transform-origin: center center;
}
#pepper_6 {
  animation: pepper_6 2s ease-in-out infinite alternate;
  transform-origin: center center;
}

@keyframes rotate {
  0% {
    transform: rotate(0deg);
  }
  100% {
    transform: rotate(360deg);
  }
}

@keyframes slice6 {
  0%, 100% {
    transform: translate(0, 0);
  }
  50% {
    transform: translate(5px, -5px);
  }
}

@keyframes slice5 {
  0%, 100% {
    transform: translate(0, 0);
  }
  50% {
    transform: translate(5px, 5px);
  }
}

@keyframes slice4 {
  0%, 100% {
    transform: translate(0, 0);
  }
  50% {
    transform: translate(-5px, 5px);
  }
}

@keyframes slice3 {
  0%, 100% {
    transform: translate(0, 0);
  }
  50% {
    transform: translate(-5px, -5px);
  }
}

@keyframes slice2 {
  0%, 100% {
    transform: translate(0, 0);
  }
  50% {
    transform: translate(0, 5px);
  }
}

@keyframes slice1 {
  0%, 100% {
    transform: translate(0, 0);
  }
  50% {
    transform: translate(0, -5px);
  }
}

@keyframes pepperoni {
  0%, 100% {
    transform: translate(0, 0);
  }
  50% {
    transform: translate(-2px, -2px);
  }
}
@keyframes pepperoni_2 {
  0%, 100% {
    transform: translate(0, 0);
  }
  50% {
    transform: translate(2px, -2px);
  }
}
@keyframes pepperoni_3 {
  0%, 100% {
    transform: translate(0, 0);
  }
  50% {
    transform: translate(-2px, 2px);
  }
}
@keyframes pepperoni_4 {
  0%, 100% {
    transform: translate(0, 0);
  }
  50% {
    transform: translate(2px, 2px);
  }
}
@keyframes pepperoni_5 {
  0%, 100% {
    transform: translate(0, 0);
  }
  50% {
    transform: translate(-2px, 0);
  }
}
@keyframes pepperoni_6 {
  0%, 100% {
    transform: translate(0, 0);
  }
  50% {
    transform: translate(2px, 0);
  }
}

@keyframes mushroom {
  0%, 100% {
    transform: translate(0, 0);
  }
  50% {
    transform: translate(-1px, -1px);
  }
}
@keyframes mushroom_2 {
  0%, 100% {
    transform: translate(0, 0);
  }
  50% {
    transform: translate(1px, -1px);
  }
}
@keyframes mushroom_3 {
  0%, 100% {
    transform: translate(0, 0);
  }
  50% {
    transform: translate(-1px, 1px);
  }
}
@keyframes mushroom_4 {
  0%, 100% {
    transform: translate(0, 0);
  }
  50% {
    transform: translate(1px, 1px);
  }
}
@keyframes mushroom_5 {
  0%, 100% {
    transform: translate(0, 0);
  }
  50% {
    transform: translate(0, -1px);
  }
}

@keyframes onion {
  0%, 100% {
    transform: translate(0, 0);
  }
  50% {
    transform: translate(-0.5px, -0.5px);
  }
}
@keyframes onion_2 {
  0%, 100% {
    transform: translate(0, 0);
  }
  50% {
    transform: translate(0.5px, -0.5px);
  }
}
@keyframes onion_3 {
  0%, 100% {
    transform: translate(0, 0);
  }
  50% {
    transform: translate(-0.5px, 0.5px);
  }
}
@keyframes onion_4 {
  0%, 100% {
    transform: translate(0, 0);
  }
  50% {
    transform: translate(0.5px, 0.5px);
  }
}
@keyframes onion_5 {
  0%, 100% {
    transform: translate(0, 0);
  }
  50% {
    transform: translate(0, -0.5px);
  }
}
@keyframes onion_6 {
  0%, 100% {
    transform: translate(0, 0);
  }
  50% {
    transform: translate(0, 0.5px);
  }
}

@keyframes pepper {
  0%, 100% {
    transform: translate(0, 0);
  }
  50% {
    transform: translate(-1.5px, -1.5px);
  }
}
@keyframes pepper_2 {
  0%, 100% {
    transform: translate(0, 0);
  }
  50% {
    transform: translate(1.5px, -1.5px);
  }
}
@keyframes pepper_3 {
  0%, 100% {
    transform: translate(0, 0);
  }
  50% {
    transform: translate(-1.5px, 1.5px);
  }
}
@keyframes pepper_4 {
  0%, 100% {
    transform: translate(0, 0);
  }
  50% {
    transform: translate(1.5px, 1.5px);
  }
}
@keyframes pepper_5 {
  0%, 100% {
    transform: translate(0, 0);
  }
  50% {
    transform: translate(-1.5px, 0);
  }
}
@keyframes pepper_6 {
  0%, 100% {
    transform: translate(0, 0);
  }
  50% {
    transform: translate(1.5px, 0);
  }
}

/* Water Wave Effect Styles */
.e-card {
  margin: 100px auto;
  background: transparent;
  box-shadow: 0px 8px 28px -9px rgba(0,0,0,0.45);
  position: relative;
  width: 240px;
  height: 330px;
  border-radius: 16px;
  overflow: hidden;
}

.wave {
  position: absolute;
  width: 540px;
  height: 700px;
  opacity: 0.6;
  left: 0;
  top: 0;
  margin-left: -50%;
  margin-top: -70%;
  background: linear-gradient(744deg,#af40ff,#5b42f3 60%,#00ddeb);
}

.icon {
  width: 3em;
  margin-top: -1em;
  padding-bottom: 1em;
}

.infotop {
  text-align: center;
  font-size: 20px;
  position: absolute;
  top: 5.6em;
  left: 0;
  right: 0;
  color: rgb(255, 255, 255);
  font-weight: 600;
}

.name {
  font-size: 14px;
  font-weight: 100;
  position: relative;
  top: 1em;
  text-transform: lowercase;
}

.wave:nth-child(2),
.wave:nth-child(3) {
  top: 210px;
}

.playing .wave {
  border-radius: 40%;
  animation: wave 3000ms infinite linear;
}

.wave {
  border-radius: 40%;
  animation: wave 55s infinite linear;
}

.playing .wave:nth-child(2) {
  animation-duration: 4000ms;
}

.wave:nth-child(2) {
  animation-duration: 50s;
}

.playing .wave:nth-child(3) {
  animation-duration: 5000ms;
}

.wave:nth-child(3) {
  animation-duration: 45s;
}

@keyframes wave {
  0% {
    transform: rotate(0deg);
  }

  100% {
    transform: rotate(360deg);
  }
}

</style>
