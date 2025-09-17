import React, { useState, useEffect } from 'react';
import { Upload, Download, Trash2, Folder, FileText, Image, Video, Music, Archive, Eye, Share2, Copy, AlertCircle } from 'lucide-react';
import { useDropzone } from 'react-dropzone';
import { toast } from 'sonner';
import { api } from '@/lib/api';
import { formatFileSize, formatDate } from '@/lib/utils';

interface FileUpload {
  file_id: string;
  filename: string;
  file_url: string;
  file_size: number;
  content_type: string;
  provider: string;
  folder: string;
  upload_date: string;
}

interface FileManagerProps {
  userId?: string;
  folder?: string;
  onFileSelect?: (file: FileUpload) => void;
}

export const FileManager: React.FC<FileManagerProps> = ({
  userId,
  folder,
  onFileSelect
}) => {
  const [files, setFiles] = useState<FileUpload[]>([]);
  const [loading, setLoading] = useState(false);
  const [uploading, setUploading] = useState(false);
  const [selectedFiles, setSelectedFiles] = useState<string[]>([]);
  const [currentFolder, setCurrentFolder] = useState(folder || 'uploads');
  const [folders, setFolders] = useState<string[]>([]);
  const [viewMode, setViewMode] = useState<'grid' | 'list'>('grid');
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedProvider, setSelectedProvider] = useState<string>('');
  const [providers, setProviders] = useState<string[]>([]);

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop: handleFileDrop,
    multiple: true,
    maxSize: 100 * 1024 * 1024, // 100MB
  });

  useEffect(() => {
    loadFiles();
    loadFolders();
    loadProviders();
  }, [currentFolder, userId]);

  const loadFiles = async () => {
    try {
      setLoading(true);
      const endpoint = userId ? `/files/all-files` : `/files/my-files`;
      const response = await api.get(endpoint, {
        params: { folder: currentFolder, limit: 100 }
      });
      setFiles(response.data.files || []);
    } catch (error) {
      toast.error('Failed to load files');
    } finally {
      setLoading(false);
    }
  };

  const loadFolders = async () => {
    try {
      const response = await api.get('/files/folders');
      setFolders(response.data.folders || []);
    } catch (error) {
      console.error('Failed to load folders:', error);
    }
  };

  const loadProviders = async () => {
    try {
      const response = await api.get('/files/providers');
      setProviders(response.data.providers || []);
    } catch (error) {
      console.error('Failed to load providers:', error);
    }
  };

  async function handleFileDrop(acceptedFiles: File[]) {
    if (acceptedFiles.length === 0) return;

    setUploading(true);
    try {
      const formData = new FormData();
      acceptedFiles.forEach(file => {
        formData.append('files', file);
      });
      formData.append('folder', currentFolder);
      if (selectedProvider) {
        formData.append('provider', selectedProvider);
      }

      const response = await api.post('/files/upload-multiple', formData, {
        headers: { 'Content-Type': 'multipart/form-data' }
      });

      toast.success(`${response.data.total_uploaded} files uploaded successfully`);
      loadFiles();
      loadFolders();
    } catch (error) {
      toast.error('Failed to upload files');
    } finally {
      setUploading(false);
    }
  }

  const handleDelete = async (fileId: string) => {
    if (!confirm('Are you sure you want to delete this file?')) return;

    try {
      await api.delete(`/files/${fileId}`);
      toast.success('File deleted successfully');
      loadFiles();
    } catch (error) {
      toast.error('Failed to delete file');
    }
  };

  const handleDownload = async (file: FileUpload) => {
    try {
      const response = await api.get(`/files/download/${file.file_id}`, {
        params: { expires_in: 3600 }
      });
      window.open(response.data.download_url, '_blank');
    } catch (error) {
      toast.error('Failed to generate download link');
    }
  };

  const handleSelectFile = (fileId: string) => {
    if (selectedFiles.includes(fileId)) {
      setSelectedFiles(selectedFiles.filter(id => id !== fileId));
    } else {
      setSelectedFiles([...selectedFiles, fileId]);
    }
  };

  const getFileIcon = (contentType: string) => {
    if (contentType.startsWith('image/')) return <Image className="w-5 h-5" />;
    if (contentType.startsWith('video/')) return <Video className="w-5 h-5" />;
    if (contentType.startsWith('audio/')) return <Music className="w-5 h-5" />;
    if (contentType.includes('zip') || contentType.includes('archive')) return <Archive className="w-5 h-5" />;
    return <FileText className="w-5 h-5" />;
  };

  const filteredFiles = files.filter(file =>
    file.filename.toLowerCase().includes(searchQuery.toLowerCase())
  );

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4">
        <div>
          <h2 className="text-2xl font-bold">File Manager</h2>
          <p className="text-gray-600">Manage your uploaded files and folders</p>
        </div>
        
        <div className="flex gap-2">
          <button
            onClick={() => setViewMode(viewMode === 'grid' ? 'list' : 'grid')}
            className="px-3 py-2 bg-gray-100 rounded-md hover:bg-gray-200 transition-colors"
          >
            {viewMode === 'grid' ? 'List View' : 'Grid View'}
          </button>
        </div>
      </div>

      {/* Controls */}
      <div className="flex flex-col sm:flex-row gap-4">
        <div className="flex-1">
          <input
            type="text"
            placeholder="Search files..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="w-full px-4 py-2 border rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
          />
        </div>
        
        <select
          value={currentFolder}
          onChange={(e) => setCurrentFolder(e.target.value)}
          className="px-4 py-2 border rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
        >
          <option value="uploads">Uploads</option>
          {folders.map(folder => (
            <option key={folder} value={folder}>{folder}</option>
          ))}
        </select>

        <select
          value={selectedProvider}
          onChange={(e) => setSelectedProvider(e.target.value)}
          className="px-4 py-2 border rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
        >
          <option value="">Auto-select</option>
          {providers.map(provider => (
            <option key={provider} value={provider}>{provider}</option>
          ))}
        </select>
      </div>

      {/* Upload Area */}
      <div
        {...getRootProps()}
        className={`border-2 border-dashed rounded-lg p-8 text-center cursor-pointer transition-colors ${
          isDragActive ? 'border-blue-500 bg-blue-50' : 'border-gray-300 hover:border-gray-400'
        }`}
      >
        <input {...getInputProps()} />
        <Upload className="w-12 h-12 mx-auto mb-4 text-gray-400" />
        <p className="text-gray-600">
          {isDragActive ? 'Drop files here...' : 'Drag & drop files here, or click to select'}
        </p>
        <p className="text-sm text-gray-500 mt-2">Max file size: 100MB</p>
      </div>

      {uploading && (
        <div className="bg-blue-50 border border-blue-200 rounded-md p-4">
          <div className="flex items-center">
            <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-blue-600 mr-2"></div>
            <span>Uploading files...</span>
          </div>
        </div>
      )}

      {/* Files Display */}
      {loading ? (
        <div className="text-center py-8">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600 mx-auto"></div>
          <p className="mt-2 text-gray-600">Loading files...</p>
        </div>
      ) : filteredFiles.length === 0 ? (
        <div className="text-center py-8">
          <Folder className="w-16 h-16 mx-auto mb-4 text-gray-400" />
          <p className="text-gray-600">No files found</p>
        </div>
      ) : (
        <div className={viewMode === 'grid' ? 'grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-4' : 'space-y-2'}>
          {filteredFiles.map(file => (
            <div
              key={file.file_id}
              className={`border rounded-lg p-4 hover:shadow-md transition-shadow ${
                selectedFiles.includes(file.file_id) ? 'ring-2 ring-blue-500' : ''
              }`}
            >
              {viewMode === 'grid' ? (
                <div className="space-y-3">
                  <div className="flex items-center justify-between">
                    <div className="flex items-center space-x-2">
                      {getFileIcon(file.content_type)}
                      <span className="text-sm font-medium truncate">{file.filename}</span>
                    </div>
                  </div>
                  
                  <div className="text-sm text-gray-600">
                    <p>{formatFileSize(file.file_size)}</p>
                    <p className="text-xs">{formatDate(file.upload_date)}</p>
                  </div>
                  
                  <div className="flex justify-between items-center">
                    <span className="text-xs bg-gray-100 px-2 py-1 rounded">{file.provider}</span>
                    <div className="flex space-x-1">
                      <button
                        onClick={() => handleDownload(file)}
                        className="p-1 hover:bg-gray-100 rounded"
                        title="Download"
                      >
                        <Download className="w-4 h-4" />
                      </button>
                      <button
                        onClick={() => handleDelete(file.file_id)}
                        className="p-1 hover:bg-red-100 rounded text-red-600"
                        title="Delete"
                      >
                        <Trash2 className="w-4 h-4" />
                      </button>
                    </div>
                  </div>
                </div>
              ) : (
                <div className="flex items-center justify-between">
                  <div className="flex items-center space-x-3">
                    {getFileIcon(file.content_type)}
                    <div>
                      <p className="font-medium">{file.filename}</p>
                      <p className="text-sm text-gray-600">
                        {formatFileSize(file.file_size)} • {formatDate(file.upload_date)}
                      </p>
                    </div>
                  </div>
                  
                  <div className="flex items-center space-x-2">
                    <span className="text-xs bg-gray-100 px-2 py-1 rounded">{file.provider}</span>
                    <button
                      onClick={() => handleDownload(file)}
                      className="p-2 hover:bg-gray-100 rounded"
                      title="Download"
                    >
                      <Download className="w-4 h-4" />
                    </button>
                    <button
                      onClick={() => handleDelete(file.file_id)}
                      className="p-2 hover:bg-red-100 rounded text-red-600"
                      title="Delete"
                    >
                      <Trash2 className="w-4 h-4" />
                    </button>
                  </div>
                </div>
              )}
            </div>
          ))}
        </div>
      )}
    </div>
  );
};