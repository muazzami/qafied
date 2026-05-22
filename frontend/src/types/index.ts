export interface User {
  id: number
  email: string
  full_name: string
  is_active: boolean
  created_at: string
}

export interface WorkspaceMember {
  id: number
  user_id: number
  full_name: string
  email: string
  role: 'owner' | 'admin' | 'member'
  joined_at: string
}

export interface Workspace {
  id: number
  name: string
  slug: string
  description: string | null
  owner_id: number
  max_members: number
  is_active: boolean
  created_at: string
  members: WorkspaceMember[]
}

export interface Website {
  id: number
  workspace_id: number
  name: string
  url: string
  script_key: string
  is_active: boolean
  show_feedback_by_default: boolean
  created_at: string
}

export type FeedbackType =
  | 'change'
  | 'remove'
  | 'replace'
  | 'bug'
  | 'suggestion'
  | 'other'

export type FeedbackStatus = 'new' | 'in_progress' | 'resolved' | 'closed'

export interface Feedback {
  id: number
  website_id: number
  page_url: string
  commenter_name: string | null
  commenter_email: string | null
  is_anonymous: boolean
  content: string
  feedback_type: FeedbackType
  status: FeedbackStatus
  element_selector: string | null
  x_position: number | null
  y_position: number | null
  browser_info: { name: string; version: string } | null
  os_info: { name: string; version: string } | null
  screen_width: number | null
  screen_height: number | null
  viewport_width: number | null
  viewport_height: number | null
  include_screenshot: boolean
  screenshot_path: string | null
  admin_response: string | null
  responded_at: string | null
  created_at: string
}
