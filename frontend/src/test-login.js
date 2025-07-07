// 前端登录测试脚本
// 可以在浏览器控制台中运行这个脚本来测试登录

// 登录函数
async function testLogin() {
  console.log('开始测试登录...');
  
  const email = 'admin@example.com';
  const password = 'admin123';
  
  // 创建表单数据
  const formData = new URLSearchParams();
  formData.append('username', email);
  formData.append('password', password);
  
  console.log('登录请求数据:', { username: email, password: '***' });
  console.log('登录请求URL:', 'http://localhost:8000/api/v1/users/login');
  
  try {
    // 发送请求
    const response = await fetch('http://localhost:8000/api/v1/users/login', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/x-www-form-urlencoded',
      },
      body: formData,
      credentials: 'include' // 包含凭证
    });
    
    console.log('响应状态:', response.status);
    
    if (response.ok) {
      const data = await response.json();
      console.log('登录成功!');
      console.log('响应数据:', data);
      
      // 测试获取用户资料
      if (data.access_token) {
        console.log('\n使用令牌获取用户资料...');
        
        const profileResponse = await fetch('http://localhost:8000/api/v1/users/profile', {
          headers: {
            'Authorization': `Bearer ${data.access_token}`
          },
          credentials: 'include' // 包含凭证
        });
        
        console.log('资料请求状态:', profileResponse.status);
        
        if (profileResponse.ok) {
          const profileData = await profileResponse.json();
          console.log('获取用户资料成功!');
          console.log('用户资料:', profileData);
        } else {
          console.error('获取用户资料失败!');
          console.error('错误信息:', await profileResponse.text());
        }
      }
    } else {
      console.error('登录失败!');
      console.error('错误信息:', await response.text());
    }
  } catch (error) {
    console.error('请求失败:', error);
  }
}

// 执行测试
testLogin().catch(console.error);

// 使用说明:
// 1. 在浏览器中打开前端应用
// 2. 打开开发者工具控制台
// 3. 复制此脚本并粘贴到控制台中运行
// 4. 查看控制台输出结果 