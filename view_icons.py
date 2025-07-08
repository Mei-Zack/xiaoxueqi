#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
查看食物营养表中的SVG图标
此脚本连接到diabetes_assistant数据库，查询food_nutrition表中的图标数据
"""

import mysql.connector
import os
import sys
import getpass

# 获取数据库连接信息
print("请输入数据库连接信息:")
host = input("数据库主机 (默认localhost): ") or 'localhost'
user = input("数据库用户名 (默认root): ") or 'root'
password = getpass.getpass("数据库密码: ") 
database = input("数据库名称 (默认diabetes_assistant): ") or 'diabetes_assistant'

# 连接数据库
try:
    conn = mysql.connector.connect(
        host=host,
        user=user,
        password=password,
        database=database
    )
    
    cursor = conn.cursor()
    
    # 查询记录总数
    cursor.execute('SELECT COUNT(*) FROM food_nutrition')
    result = cursor.fetchone()
    print(f'食物营养表中共有 {result[0]} 条记录')
    
    # 查询前5条记录的名称和图标URL
    cursor.execute('SELECT name_cn, image_url FROM food_nutrition LIMIT 5')
    results = cursor.fetchall()
    
    print('\n示例数据:')
    for i, row in enumerate(results):
        print(f'\n[{i+1}] 名称: {row[0]}')
        print(f'图标URL长度: {len(row[1])}字节')
        print(f'图标URL前缀: {row[1][:30]}...')
    
    # 将图标保存到HTML文件中以便查看
    if results:
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <title>食物图标预览</title>
            <style>
                .icon-container {{
                    display: flex;
                    flex-wrap: wrap;
                    gap: 20px;
                }}
                .icon-item {{
                    border: 1px solid #ccc;
                    padding: 10px;
                    border-radius: 5px;
                    width: 150px;
                    text-align: center;
                }}
                .icon {{
                    width: 100px;
                    height: 100px;
                    margin: 0 auto;
                }}
            </style>
        </head>
        <body>
            <h1>食物图标预览</h1>
            <div class="icon-container">
        """
        
        for i, row in enumerate(results):
            html_content += f"""
                <div class="icon-item">
                    <div class="icon">{row[1]}</div>
                    <p>{row[0]}</p>
                </div>
            """
        
        html_content += """
            </div>
        </body>
        </html>
        """
        
        with open('food_icons_preview.html', 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        print('\n已生成图标预览HTML文件: food_icons_preview.html')
        print('请在浏览器中打开此文件查看图标效果')
    
    conn.close()

except mysql.connector.Error as err:
    print(f"数据库错误: {err}")
except Exception as e:
    print(f"发生错误: {e}") 