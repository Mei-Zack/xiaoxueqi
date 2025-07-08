#!/usr/bin/env python
"""
开发环境设置脚本
用于快速设置开发环境，包括:
1. 初始化数据库
2. 创建超级管理员
3. 添加示例数据（可选）

使用方法:
- 初始化数据库（使用SQL文件创建所有表）: python setup_dev.py --init-db
- 初始化数据库（使用ORM模型创建表）: python setup_dev.py --init-db --use-orm
- 重置数据库（删除所有表并重新创建）: python setup_dev.py --reset
- 创建示例数据: python setup_dev.py --sample-data

注意:
- 默认使用diabetes_assistant.sql文件创建表结构，确保该文件位于backend目录下
- 使用--use-orm参数可以使用SQLAlchemy ORM模型创建表，但可能与SQL文件定义的表结构有差异
- 初始化后会创建两个账号：
  * 管理员: admin@example.com / admin123
  * 测试用户: test@example.com / admin123
"""

import os
import sys
import logging
import argparse
from datetime import datetime, timedelta
import random
import sqlalchemy

# 确保能够导入app包
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.db.init_db import init_db, reset_db
from app.db.session import SessionLocal, engine
from app.models.user import UserCreate
from app.services.user import create_superuser, get_user_by_email

# 配置日志
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)


def create_tables_from_sql():
    """从SQL文件创建所有表"""
    try:
        # 获取SQL文件路径
        sql_file_path = os.path.join(os.path.dirname(__file__), "diabetes_assistant.sql")
        
        if not os.path.exists(sql_file_path):
            logger.warning(f"SQL文件不存在: {sql_file_path}")
            return False
        
        # 读取SQL文件内容
        with open(sql_file_path, 'r', encoding='utf-8') as f:
            sql_content = f.read()
        
        # 分割SQL语句
        sql_statements = []
        current_statement = []
        
        for line in sql_content.split('\n'):
            # 跳过注释和空行
            if line.strip().startswith('--') or line.strip() == '' or line.strip().startswith('/*') or line.strip().startswith('*/'):
                continue
                
            # 添加到当前语句
            current_statement.append(line)
            
            # 如果行以分号结束，则完成一个语句
            if line.strip().endswith(';'):
                sql_statements.append('\n'.join(current_statement))
                current_statement = []
        
        # 执行SQL语句
        with engine.begin() as conn:
            # 设置外键检查为0
            conn.execute(sqlalchemy.text("SET FOREIGN_KEY_CHECKS = 0;"))
            
            for statement in sql_statements:
                if statement.strip():
                    # 只执行创建表的语句
                    if "CREATE TABLE" in statement:
                        try:
                            conn.execute(sqlalchemy.text(statement))
                            logger.info(f"已执行: {statement[:50]}...")
                        except Exception as e:
                            logger.error(f"执行SQL语句失败: {str(e)}")
            
            # 恢复外键检查
            conn.execute(sqlalchemy.text("SET FOREIGN_KEY_CHECKS = 1;"))
        
        logger.info("从SQL文件创建表完成")
        return True
    
    except Exception as e:
        logger.error(f"从SQL文件创建表失败: {str(e)}")
        return False


def create_admin_user(db):
    """创建超级管理员账户"""
    try:
        from app.db.models import User
        
        # 检查用户是否已存在
        existing_user = get_user_by_email(db, email="admin@example.com")
        if existing_user:
            logger.info(f"超级管理员账户已存在: {existing_user.email}")
            return existing_user
        
        admin = UserCreate(
            email="admin@example.com",
            name="系统管理员",
            password="admin123",
            is_active=True,
            is_superuser=True
        )
        
        user = create_superuser(db, admin)
        logger.info(f"超级管理员账户创建成功: {user.email}")
        return user
    except Exception as e:
        logger.error(f"创建超级管理员失败: {str(e)}")
        return None


def create_test_user(db):
    """创建测试用户账户"""
    try:
        from app.services.user import create_user
        
        # 检查用户是否已存在
        existing_user = get_user_by_email(db, email="test@example.com")
        if existing_user:
            logger.info(f"测试用户账户已存在: {existing_user.email}")
            return existing_user
        
        test_user = UserCreate(
            email="test@example.com",
            name="测试用户",
            password="admin123",
            is_active=True
        )
        
        user = create_user(db, test_user)
        logger.info(f"测试用户创建成功: {user.email}")
        return user
    except Exception as e:
        logger.error(f"创建测试用户失败: {str(e)}")
        return None


def create_sample_glucose_data(db, user_id, num_records=30):
    """为用户创建示例血糖数据"""
    try:
        from app.db.models import GlucoseRecord
        from app.models.glucose import MeasurementTimeEnum, MeasurementMethodEnum
        
        # 获取枚举值的实际字符串表示
        measurement_time_values = [
            MeasurementTimeEnum.FASTING,
            MeasurementTimeEnum.BEFORE_MEAL,
            MeasurementTimeEnum.AFTER_MEAL,
            MeasurementTimeEnum.BEFORE_SLEEP
        ]
        
        measurement_method_values = [
            MeasurementMethodEnum.FINGER_STICK,
            MeasurementMethodEnum.CONTINUOUS_MONITOR,
            MeasurementMethodEnum.LAB_TEST
        ]
        
        # 生成过去30天的记录
        today = datetime.now()
        
        # 随机血糖值区间
        ranges = {
            MeasurementTimeEnum.FASTING: (4.0, 7.0),  # 空腹
            MeasurementTimeEnum.BEFORE_MEAL: (4.0, 7.0),  # 餐前
            MeasurementTimeEnum.AFTER_MEAL: (5.0, 10.0),  # 餐后
            MeasurementTimeEnum.BEFORE_SLEEP: (5.0, 8.5)   # 睡前
        }
        
        records = []
        for i in range(num_records):
            # 随机日期（过去1个月内）
            days_ago = random.randint(0, 29)
            record_date = today - timedelta(days=days_ago)
            
            # 随机测量类型
            measurement_time = random.choice(measurement_time_values)
            
            # 根据测量类型生成合理范围内的血糖值
            min_val, max_val = ranges.get(measurement_time, (4.0, 10.0))
            
            # 生成正态分布的随机血糖值
            mu = (min_val + max_val) / 2
            sigma = (max_val - min_val) / 6  # 99.7%的值将在6sigma范围内
            value = random.normalvariate(mu, sigma)
            value = round(max(min_val * 0.8, min(max_val * 1.2, value)), 1)  # 限制在合理范围内并保留1位小数
            
            # 创建记录
            record = GlucoseRecord(
                user_id=user_id,
                value=value,
                measurement_time=measurement_time,
                measurement_method=random.choice(measurement_method_values),
                measured_at=record_date,
                notes=f"示例数据 #{i+1}"
            )
            records.append(record)
        
        # 批量添加记录
        db.add_all(records)
        db.commit()
        
        logger.info(f"已为用户 {user_id} 创建 {len(records)} 条示例血糖记录")
        return records
    
    except Exception as e:
        logger.error(f"创建示例血糖数据失败: {str(e)}")
        db.rollback()
        return []


def main():
    """主函数"""
    parser = argparse.ArgumentParser(description="开发环境设置")
    parser.add_argument("--reset", action="store_true", help="重置数据库（删除所有表并重新创建）")
    parser.add_argument("--sample-data", action="store_true", help="创建示例数据")
    parser.add_argument("--init-db", action="store_true", help="初始化数据库")
    parser.add_argument("--use-orm", action="store_true", help="使用ORM模型创建表结构（默认使用SQL文件）")
    args = parser.parse_args()
    
    try:
        if args.reset:
            logger.info("正在重置数据库...")
            reset_db()
        elif args.init_db or not args.sample_data:
            logger.info("正在初始化数据库...")
            if args.use_orm:
                logger.info("使用ORM模型创建表结构...")
                init_db()
            else:
                logger.info("使用SQL文件创建表结构...")
                create_tables_from_sql()
        
        db = SessionLocal()
        try:
            # 创建超级管理员
            admin = create_admin_user(db)
            
            # 创建测试用户
            test_user = create_test_user(db)
            
            # 创建示例数据
            if args.sample_data and test_user:
                logger.info("正在创建示例数据...")
                create_sample_glucose_data(db, test_user.id)
            
            logger.info("开发环境设置完成！")
            logger.info("\n开发账号信息:")
            logger.info(f"管理员: admin@example.com / admin123")
            logger.info(f"测试用户: test@example.com / admin123")
            logger.info("\n启动应用: python main.py")
        
        finally:
            db.close()
    
    except Exception as e:
        logger.error(f"设置过程中发生错误: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    main() 