export const APP_NAME = import.meta.env.VITE_APP_NAME || 'OpenLMS';
export const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || '/api/v1';

export const ALLOWED_FILE_TYPES = [
  'pdf', 'docx', 'pptx', 'xlsx', 'jpg', 'jpeg', 'png', 'zip', 'mp4', 'mp3', 'csv', 'txt'
];

export const MAX_FILE_SIZE_BYTES = 25 * 1024 * 1024; // 25 MB
