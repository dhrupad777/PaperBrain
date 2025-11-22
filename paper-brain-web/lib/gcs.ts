// Google Cloud Storage client helper
// TODO: Implement GCS integration when ready

export interface GCSConfig {
  bucketName: string;
  projectId: string;
  credentials?: string;
}

export class GCSClient {
  private config: GCSConfig;

  constructor(config: GCSConfig) {
    this.config = config;
  }

  async uploadFile(file: File, path: string): Promise<string> {
    // TODO: Implement GCS upload
    throw new Error('GCS upload not implemented yet');
  }

  async getFileUrl(path: string): Promise<string> {
    // TODO: Implement GCS URL generation
    throw new Error('GCS URL generation not implemented yet');
  }

  async deleteFile(path: string): Promise<void> {
    // TODO: Implement GCS file deletion
    throw new Error('GCS file deletion not implemented yet');
  }
}

// Singleton instance (initialize with env vars)
export const gcsClient = new GCSClient({
  bucketName: process.env.GCS_BUCKET_NAME || '',
  projectId: process.env.GCS_PROJECT_ID || '',
  credentials: process.env.GCS_CREDENTIALS,
});

