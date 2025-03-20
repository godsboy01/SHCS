// 权限配置
const permissions = {
  // 页面权限配置
  pages: {
    'home': ['admin', 'elderly', 'guardian'],
    'device-control': ['admin', 'elderly', 'guardian'],
    'health-monitor': ['admin', 'elderly', 'guardian'],
    'user-management': ['admin'],
    'family-management': ['admin', 'guardian'],
    'care-settings': ['guardian'],
    'personal-center': ['admin', 'elderly', 'guardian']
  },
  
  // 功能权限配置
  features: {
    'addDevice': ['admin'],
    'removeDevice': ['admin'],
    'modifySettings': ['admin', 'guardian'],
    'viewHealth': ['admin', 'guardian', 'elderly'],
    'manageUsers': ['admin'],
    'manageCare': ['admin', 'guardian']
  }
};

// 检查页面权限
const checkPagePermission = (pagePath, role) => {
  const page = pagePath.split('/').pop();
  return permissions.pages[page]?.includes(role) || false;
};

// 检查功能权限
const checkFeaturePermission = (feature, role) => {
  return permissions.features[feature]?.includes(role) || false;
};

export default {
  checkPagePermission,
  checkFeaturePermission,
  permissions
}; 