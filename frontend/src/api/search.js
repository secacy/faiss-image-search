import request from "./request";

// 搜索API
export const searchApi = {
  // 通过上传文件搜索
  searchByUpload: (formData) => {
    return request.post("/search/by-upload", formData, {
      headers: {
        "Content-Type": "multipart/form-data",
      },
    });
  },

  // 通过URL搜索
  searchByUrl: (formData) => {
    return request.post("/search/by-url", formData, {
      headers: {
        "Content-Type": "multipart/form-data",
      },
    });
  },

  // 通过图片ID搜索
  searchByImageId: (imageId, params) => {
    return request.post(`/search/by-image-id/${imageId}`, params, {
      headers: {
        "Content-Type": "multipart/form-data",
      },
    });
  },
};

// 单独导出函数以兼容其他组件
export const searchByFile = searchApi.searchByUpload;
export const searchByUrl = (url, params) => {
  const formData = new FormData();
  formData.append("image_url", url); 
  if (params.top_k) formData.append("k", params.top_k); 
  if (params.threshold) formData.append("threshold", params.threshold);
  return searchApi.searchByUrl(formData);
};
export const searchByImageId = searchApi.searchByImageId;

// 图片相关API
export const getImages = (params) => {
  return request.get("/images/list", { params });
};

// 图片管理API
export const imageApi = {
  // 获取图片列表
  getImages: (params) => {
    return request.get("/images/list", { params });
  },

  // 上传图片
  uploadImage: (formData) => {
    return request.post("/images/upload", formData, {
      headers: {
        "Content-Type": "multipart/form-data",
      },
    });
  },

  // 获取图片详情
  getImageDetail: (imageId) => {
    return request.get(`/images/${imageId}`);
  },

  // 删除图片
  deleteImage: (imageId) => {
    return request.delete(`/images/${imageId}`);
  },

  // 更新图片信息
  updateImage: (imageId, data) => {
    return request.put(`/images/${imageId}`, data);
  },

  // 获取图片统计
  getImageStats: () => {
    return request.get("/images/stats/summary");
  },

  // 管理后台相关接口
  admin: {
    // 获取仪表板统计
    getDashboardStats: () => {
      return request.get("/admin/dashboard");
    },

    // 获取图片详细统计
    getImageStats: () => {
      return request.get("/admin/images/stats");
    },

    // 获取系统信息
    getSystemInfo: () => {
      return request.get("/admin/system/info");
    },

    // 系统配置相关
    config: {
      // 获取所有配置
      getAll: () => {
        return request.get("/admin/config");
      },

      // 更新配置
      update: (configData) => {
        return request.post("/admin/config", configData);
      },

      // 获取单个配置
      get: (configKey) => {
        return request.get(`/admin/config/${configKey}`);
      },

      // 更新单个配置
      updateSingle: (configKey, data) => {
        return request.put(`/admin/config/${configKey}`, data);
      },
    },

    // 系统操作
    system: {
      // 重启系统
      restart: () => {
        return request.post("/admin/system/restart");
      },

      // 清理缓存
      clearCache: () => {
        return request.post("/admin/system/cache/clear");
      },

      // 重建索引
      rebuildIndex: () => {
        return request.post("/admin/index/rebuild");
      },
    },
  },
};
