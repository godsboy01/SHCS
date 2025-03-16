// utils/api.js

const BASE_URL = 'http://127.0.0.1:5000/api'; // 替换为实际服务器地址

export const createFamily = (familyName) => {
  return wx.request({
    url: `${BASE_URL}/family/create_family`,
    method: 'POST',
    data: { family_name: familyName },
    header: { 'content-type': 'application/json' }
  });
};

export const addMember = (data) => {
  return wx.request({
    url: `${BASE_URL}/family/add_member`,
    method: 'POST',
    data,
    header: { 'content-type': 'application/json' }
  });
};

export const getFamilyMembers = (familyId) => {
  return wx.request({
    url: `${BASE_URL}/family/get_members/${familyId}`,
    method: 'GET',
    header: { 'content-type': 'application/json' }
  });
};

export const updateMember = (userId, data) => {
  return wx.request({
    url: `${BASE_URL}/family/update_member/${userId}`,
    method: 'PUT',
    data,
    header: { 'content-type': 'application/json' }
  });
};

export const deleteMember = (userId) => {
  return wx.request({
    url: `${BASE_URL}/family/delete_member/${userId}`,
    method: 'DELETE',
    header: { 'content-type': 'application/json' }
  });
};