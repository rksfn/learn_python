-- Database schema for Task Management System

-- Users table
CREATE TABLE users (
    user_id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT NOT NULL UNIQUE,
    email TEXT NOT NULL UNIQUE,
    password_hash TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_login TIMESTAMP,
    is_active BOOLEAN DEFAULT TRUE
);

-- Projects table
CREATE TABLE projects (
    project_id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,
    description TEXT,
    owner_id INTEGER NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    is_archived BOOLEAN DEFAULT FALSE,
    FOREIGN KEY (owner_id) REFERENCES users(user_id)
);

-- Tasks table
CREATE TABLE tasks (
    task_id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,
    description TEXT,
    project_id INTEGER NOT NULL,
    assigned_to INTEGER,
    created_by INTEGER NOT NULL,
    status TEXT DEFAULT 'pending' CHECK(status IN ('pending', 'in_progress', 'completed', 'cancelled')),
    priority INTEGER DEFAULT 1 CHECK(priority BETWEEN 1 AND 5),
    due_date TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (project_id) REFERENCES projects(project_id),
    FOREIGN KEY (assigned_to) REFERENCES users(user_id),
    FOREIGN KEY (created_by) REFERENCES users(user_id)
);

-- Comments table
CREATE TABLE comments (
    comment_id INTEGER PRIMARY KEY AUTOINCREMENT,
    task_id INTEGER NOT NULL,
    user_id INTEGER NOT NULL,
    content TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (task_id) REFERENCES tasks(task_id),
    FOREIGN KEY (user_id) REFERENCES users(user_id)
);

-- Attachments table
CREATE TABLE attachments (
    attachment_id INTEGER PRIMARY KEY AUTOINCREMENT,
    task_id INTEGER NOT NULL,
    filename TEXT NOT NULL,
    file_path TEXT NOT NULL,
    file_size INTEGER NOT NULL,
    mime_type TEXT NOT NULL,
    uploaded_by INTEGER NOT NULL,
    uploaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (task_id) REFERENCES tasks(task_id),
    FOREIGN KEY (uploaded_by) REFERENCES users(user_id)
);

-- Project members table (many-to-many relationship between users and projects)
CREATE TABLE project_members (
    project_id INTEGER NOT NULL,
    user_id INTEGER NOT NULL,
    role TEXT DEFAULT 'member' CHECK(role IN ('owner', 'admin', 'member', 'viewer')),
    joined_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (project_id, user_id),
    FOREIGN KEY (project_id) REFERENCES projects(project_id),
    FOREIGN KEY (user_id) REFERENCES users(user_id)
);

-- Task activities for tracking history
CREATE TABLE task_activities (
    activity_id INTEGER PRIMARY KEY AUTOINCREMENT,
    task_id INTEGER NOT NULL,
    user_id INTEGER NOT NULL,
    action TEXT NOT NULL,
    details TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (task_id) REFERENCES tasks(task_id),
    FOREIGN KEY (user_id) REFERENCES users(user_id)
);

-- Tags table
CREATE TABLE tags (
    tag_id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL UNIQUE,
    color TEXT DEFAULT '#cccccc'
);

-- Task-Tag relationship (many-to-many)
CREATE TABLE task_tags (
    task_id INTEGER NOT NULL,
    tag_id INTEGER NOT NULL,
    PRIMARY KEY (task_id, tag_id),
    FOREIGN KEY (task_id) REFERENCES tasks(task_id),
    FOREIGN KEY (tag_id) REFERENCES tags(tag_id)
);

-- Add indexes for better query performance
CREATE INDEX idx_tasks_project_id ON tasks(project_id);
CREATE INDEX idx_tasks_assigned_to ON tasks(assigned_to);
CREATE INDEX idx_tasks_status ON tasks(status);
CREATE INDEX idx_tasks_due_date ON tasks(due_date);
CREATE INDEX idx_comments_task_id ON comments(task_id);
CREATE INDEX idx_attachments_task_id ON attachments(task_id);
CREATE INDEX idx_task_activities_task_id ON task_activities(task_id);

-- Insert some sample data

-- Users
INSERT INTO users (username, email, password_hash, is_active) VALUES 
('admin', 'admin@example.com', 'pbkdf2:sha256:150000$LDYcGCiW$b43457a546a8aaa7d9c5de5e6592a2022adadf8b02cb553cb7c7e4e3148cd6dd', TRUE),
('john_doe', 'john@example.com', 'pbkdf2:sha256:150000$rDgTlb7Z$2b22d8e30fef42ba5b71072ba02ba978be15e8be8f791abfcb5bd850a7ba0835', TRUE),
('jane_smith', 'jane@example.com', 'pbkdf2:sha256:150000$Ih2r95KL$1ab52a5c895ea7ec1b1244739d6100bbe9c3e0f2ca3ee27a8da8e509e36fb2ae', TRUE),
('bob_jackson', 'bob@example.com', 'pbkdf2:sha256:150000$UKrQlGIc$495e48565c8e5dce92b0dec88e8b8ac88a54dce2ee6f1dbd0423117f4a0738fa', FALSE);

-- Projects
INSERT INTO projects (title, description, owner_id) VALUES
('Website Redesign', 'Redesign company website with modern UI/UX', 1),
('Mobile App Development', 'Develop iOS and Android app for customers', 2),
('Database Migration', 'Migrate from MySQL to PostgreSQL', 1),
('Marketing Campaign', 'Q4 marketing campaign planning and execution', 3);

-- Project Members
INSERT INTO project_members (project_id, user_id, role) VALUES
(1, 1, 'owner'), (1, 2, 'member'), (1, 3, 'viewer'),
(2, 2, 'owner'), (2, 1, 'admin'), (2, 3, 'member'),
(3, 1, 'owner'), (3, 2, 'member'),
(4, 3, 'owner'), (4, 1, 'viewer');

-- Tasks
INSERT INTO tasks (title, description, project_id, assigned_to, created_by, status, priority, due_date) VALUES
('Design homepage mockup', 'Create wireframes and design mockups for the new homepage', 1, 2, 1, 'in_progress', 3, datetime('now', '+10 days')),
('Setup development environment', 'Configure development servers and CI/CD pipeline', 1, 1, 1, 'completed', 2, datetime('now', '-5 days')),
('Implement user authentication', 'Add login/registration flow to the website', 1, 2, 1, 'pending', 4, datetime('now', '+15 days')),

('Create app wireframes', 'Design initial wireframes for mobile app', 2, 3, 2, 'completed', 2, datetime('now', '-20 days')),
('Develop login screen', 'Implement user login screen with social media integration', 2, 2, 2, 'in_progress', 3, datetime('now', '+5 days')),
('Implement push notifications', 'Add support for push notifications', 2, null, 2, 'pending', 1, datetime('now', '+25 days')),

('Analyze current database schema', 'Document current MySQL schema and identify migration challenges', 3, 1, 1, 'completed', 5, datetime('now', '-15 days')),
('Create migration scripts', 'Develop scripts to migrate data from MySQL to PostgreSQL', 3, 2, 1, 'in_progress', 5, datetime('now', '+3 days')),
('Test migration process', 'Run test migrations and verify data integrity', 3, null, 1, 'pending', 4, datetime('now', '+10 days')),

('Create marketing materials', 'Design flyers, social media posts, and email templates', 4, 3, 3, 'in_progress', 3, datetime('now', '+7 days')),
('Plan launch event', 'Organize product launch event for Q4 campaign', 4, 3, 3, 'pending', 2, datetime('now', '+30 days'));

-- Comments
INSERT INTO comments (task_id, user_id, content) VALUES
(1, 1, 'Please use the brand color palette provided in the design system'),
(1, 2, 'I''ve started working on the mockups, will share a draft by tomorrow'),
(2, 1, 'Environment setup completed, you can now start development'),
(4, 2, 'The wireframes look good! Let''s proceed with the development'),
(4, 3, 'I''ve added some annotations to the wireframes for clarification'),
(5, 1, 'Make sure we support both biometric and traditional login methods'),
(7, 2, 'I found some potential issues with the foreign key constraints'),
(8, 1, 'Let''s schedule a meeting to discuss the migration strategy');

-- Tags
INSERT INTO tags (name, color) VALUES
('UI/UX', '#ff7700'),
('Backend', '#00aaff'),
('Database', '#aa00ff'),
('Frontend', '#ffaa00'),
('Mobile', '#00ff7f'),
('Urgent', '#ff0000'),
('Documentation', '#aaaaaa');

-- Task Tags
INSERT INTO task_tags (task_id, tag_id) VALUES
(1, 1), (1, 4),
(2, 2), (2, 3),
(3, 2), (3, 4),
(4, 1), (4, 5),
(5, 4), (5, 5),
(6, 2), (6, 5),
(7, 3), (7, 7),
(8, 2), (8, 3), (8, 6),
(9, 3), (9, 7),
(10, 1), (10, 7),
(11, 7);

-- Attachments
INSERT INTO attachments (task_id, filename, file_path, file_size, mime_type, uploaded_by) VALUES
(1, 'brand_guidelines.pdf', '/uploads/files/brand_guidelines.pdf', 2457862, 'application/pdf', 1),
(1, 'homepage_draft.png', '/uploads/files/homepage_draft.png', 1458723, 'image/png', 2),
(4, 'app_wireframes.sketch', '/uploads/files/app_wireframes.sketch', 3287456, 'application/octet-stream', 3),
(7, 'database_schema.sql', '/uploads/files/database_schema.sql', 15487, 'text/plain', 1),
(10, 'marketing_calendar.xlsx', '/uploads/files/marketing_calendar.xlsx', 587452, 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet', 3);

-- Task Activities
INSERT INTO task_activities (task_id, user_id, action, details) VALUES
(1, 1, 'created', 'Task created'),
(1, 2, 'updated', 'Changed status to in_progress'),
(2, 1, 'created', 'Task created'),
(2, 1, 'updated', 'Changed status to completed'),
(3, 1, 'created', 'Task created'),
(4, 2, 'created', 'Task created'),
(4, 3, 'updated', 'Changed status to completed'),
(5, 2, 'created', 'Task created'),
(5, 2, 'updated', 'Changed status to in_progress'),
(6, 2, 'created', 'Task created'),
(7, 1, 'created', 'Task created'),
(7, 1, 'updated', 'Changed status to completed'),
(8, 1, 'created', 'Task created'),
(8, 2, 'updated', 'Changed status to in_progress'),
(9, 1, 'created', 'Task created'),
(10, 3, 'created', 'Task created'),
(10, 3, 'updated', 'Changed status to in_progress'),
(11, 3, 'created', 'Task created');
