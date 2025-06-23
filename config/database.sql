-- 图与图寻数据库初始化脚本

-- 创建数据库
CREATE DATABASE IF NOT EXISTS pic_search CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE pic_search;

-- 用户表
CREATE TABLE IF NOT EXISTS users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    email VARCHAR(100),
    role ENUM('admin', 'user') DEFAULT 'user',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    is_active BOOLEAN DEFAULT TRUE
);

-- 图片信息表
CREATE TABLE IF NOT EXISTS images (
    id INT AUTO_INCREMENT PRIMARY KEY,
    filename VARCHAR(255) NOT NULL,
    original_name VARCHAR(255) NOT NULL,
    file_path VARCHAR(500) NOT NULL,
    file_size BIGINT NOT NULL,
    width INT,
    height INT,
    format VARCHAR(10),
    hash_value VARCHAR(64) UNIQUE,
    faiss_id INT UNIQUE,
    upload_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    upload_by INT,
    tags JSON,
    description TEXT,
    is_active BOOLEAN DEFAULT TRUE,
    INDEX idx_faiss_id (faiss_id),
    INDEX idx_hash_value (hash_value),
    INDEX idx_upload_time (upload_time),
    FOREIGN KEY (upload_by) REFERENCES users(id) ON DELETE SET NULL
);



-- Faiss索引信息表
CREATE TABLE IF NOT EXISTS faiss_index_info (
    id INT AUTO_INCREMENT PRIMARY KEY,
    index_path VARCHAR(500) NOT NULL,
    total_vectors INT DEFAULT 0,
    feature_dim INT DEFAULT 2048,
    index_type VARCHAR(50) DEFAULT 'IndexFlatIP',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    is_current BOOLEAN DEFAULT TRUE
);

-- 系统配置表
CREATE TABLE IF NOT EXISTS system_config (
    id INT AUTO_INCREMENT PRIMARY KEY,
    config_key VARCHAR(100) UNIQUE NOT NULL,
    config_value TEXT,
    description VARCHAR(255),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

-- 操作日志表
CREATE TABLE IF NOT EXISTS operation_logs (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT,
    operation VARCHAR(50) NOT NULL,
    resource_type VARCHAR(50),
    resource_id INT,
    details JSON,
    ip_address VARCHAR(45),
    user_agent TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_user_id (user_id),
    INDEX idx_operation (operation),
    INDEX idx_created_at (created_at),
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE SET NULL
);

-- 插入默认管理员用户
INSERT INTO users (username, password_hash, email, role) VALUES
('admin', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewrukmOPcF/Zs0ZS', 'admin@example.com', 'admin');
-- 密码: admin123

-- 插入系统配置
INSERT INTO system_config (config_key, config_value, description) VALUES
('max_upload_size', '10485760', '最大上传文件大小（字节）'),
('allowed_file_types', '["jpg", "jpeg", "png", "bmp", "webp"]', '允许的文件类型'),
('default_search_k', '10', '默认搜索返回结果数量'),
('max_search_k', '100', '最大搜索返回结果数量');

-- 创建初始Faiss索引记录
INSERT INTO faiss_index_info (index_path, total_vectors, feature_dim, index_type) VALUES
('data/index/image_features.index', 0, 2048, 'IndexFlatIP'); 