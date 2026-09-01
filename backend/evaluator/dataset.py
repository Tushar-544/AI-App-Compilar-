"""Evaluation dataset — 10 real prompts + 10 edge cases."""

REAL_PROMPTS = [
    {
        "id": "real_01",
        "label": "CRM with payments",
        "prompt": "Build a CRM with login, contacts, deals pipeline, role-based access for admin and sales reps, dashboard with analytics, and premium plan with Stripe payments."
    },
    {
        "id": "real_02",
        "label": "E-commerce store",
        "prompt": "Create an e-commerce platform with product catalog, shopping cart, checkout with payments, order tracking, admin dashboard for inventory, and customer accounts."
    },
    {
        "id": "real_03",
        "label": "Learning Management System",
        "prompt": "Build an LMS where instructors can create courses with videos and quizzes, students enroll and track progress, and admins manage the platform. Include certificates on completion."
    },
    {
        "id": "real_04",
        "label": "Project Management Tool",
        "prompt": "Create a project management app like Trello with boards, lists, cards, team collaboration, file attachments, due dates, comments, and role-based permissions."
    },
    {
        "id": "real_05",
        "label": "Hospital Management",
        "prompt": "Build a hospital management system with patient records, doctor scheduling, appointment booking, pharmacy inventory, billing, and role-based access for doctors, nurses, and admin."
    },
    {
        "id": "real_06",
        "label": "Blog Platform",
        "prompt": "Create a multi-author blog platform with rich text editor, categories, tags, comments with moderation, SEO tools, newsletter subscription, and admin dashboard."
    },
    {
        "id": "real_07",
        "label": "Social Network",
        "prompt": "Build a social network with user profiles, posts with media, follow system, news feed, direct messaging, notifications, and content moderation tools for admins."
    },
    {
        "id": "real_08",
        "label": "Restaurant Booking",
        "prompt": "Create a restaurant booking system with table reservations, menu management, customer reviews, loyalty points, staff scheduling, and real-time availability."
    },
    {
        "id": "real_09",
        "label": "Inventory Management",
        "prompt": "Build an inventory management system with products, categories, stock tracking, purchase orders, suppliers, low-stock alerts, barcode scanning, and reports."
    },
    {
        "id": "real_10",
        "label": "HR Tool",
        "prompt": "Create an HR platform with employee profiles, leave management, payroll, performance reviews, recruitment pipeline, org chart, and role-based access for HR, managers, and employees."
    },
]

EDGE_CASES = [
    {
        "id": "edge_01",
        "label": "Vague: minimal info",
        "prompt": "Build me an app.",
        "expected_behavior": "Should ask for clarification or make reasonable assumptions and document them"
    },
    {
        "id": "edge_02",
        "label": "Conflicting: free + paid",
        "prompt": "Build a free app with premium features but no payment system.",
        "expected_behavior": "Should detect conflict between 'free' and 'premium features', resolve by assuming freemium model"
    },
    {
        "id": "edge_03",
        "label": "Incomplete: no roles",
        "prompt": "CRM with login.",
        "expected_behavior": "Should assume standard roles (admin, user) and basic CRUD features"
    },
    {
        "id": "edge_04",
        "label": "Overspecified: 500 words",
        "prompt": "Build a SaaS platform with multi-tenancy, white-labeling, SSO with Google and GitHub, 2FA, audit logs, granular RBAC with 15 permission types, real-time collaboration, offline mode, mobile apps for iOS and Android, REST and GraphQL APIs, webhooks, Zapier integration, custom domain support, Stripe and PayPal payments, usage-based billing, metered API access, AI-powered analytics with ML predictions, drag-and-drop report builder, data export to CSV/Excel/PDF, email notifications with templates, in-app notifications, Slack and Teams integration, advanced search with Elasticsearch, full-text search, geolocation features, file storage with S3, CDN support, dark mode, i18n for 20 languages, accessibility (WCAG 2.1 AA), GDPR compliance tools, data retention policies, automated backups, disaster recovery, 99.99% SLA, horizontal scaling, microservices architecture, Docker and Kubernetes deployment, CI/CD pipeline, feature flags, A/B testing, session recording, heatmaps, and a customer-facing status page.",
        "expected_behavior": "Should handle gracefully, prioritize core features, document what's out of scope"
    },
    {
        "id": "edge_05",
        "label": "Ambiguous: unclear entities",
        "prompt": "Build a system for managing things with users and stuff.",
        "expected_behavior": "Should identify ambiguities and make documented assumptions"
    },
    {
        "id": "edge_06",
        "label": "Contradictory roles",
        "prompt": "Build an app where all users are admins and no one needs permissions.",
        "expected_behavior": "Should resolve contradiction by creating a single superuser role"
    },
    {
        "id": "edge_07",
        "label": "Single entity",
        "prompt": "Build a todo list app.",
        "expected_behavior": "Should generate minimal but complete schema for a simple app"
    },
    {
        "id": "edge_08",
        "label": "Technical jargon only",
        "prompt": "Build a microservices event-driven CQRS system with eventual consistency and saga pattern.",
        "expected_behavior": "Should interpret technical requirements and generate appropriate schemas"
    },
    {
        "id": "edge_09",
        "label": "Non-software request",
        "prompt": "Build me a sandwich.",
        "expected_behavior": "Should gracefully handle non-software prompts with appropriate error"
    },
    {
        "id": "edge_10",
        "label": "Mixed language",
        "prompt": "Build an app de gestion des contacts avec login et dashboard pour les admins.",
        "expected_behavior": "Should handle non-English prompts and generate English schemas"
    },
]

ALL_PROMPTS = REAL_PROMPTS + EDGE_CASES
