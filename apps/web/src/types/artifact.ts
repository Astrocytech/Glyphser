export type ArtifactEntry = {
  path: string
  contentType: string
}

export type ArtifactFileResponse = ArtifactEntry & {
  content: string
}

