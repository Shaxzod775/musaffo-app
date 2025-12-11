const API_BASE_URL = (typeof (import.meta as any).env !== 'undefined' && (import.meta as any).env.VITE_API_URL) || 'https://musaffo-core-api-242593050011.us-central1.run.app';

// News API
export const newsApi = {
    getAll: async () => {
        const response = await fetch(`${API_BASE_URL}/api/news`);
        if (!response.ok) throw new Error('Failed to fetch news');
        return response.json();
    },

    getById: async (id: string) => {
        const response = await fetch(`${API_BASE_URL}/api/news/${id}`);
        if (!response.ok) throw new Error('Failed to fetch news');
        return response.json();
    },

    create: async (newsData: any) => {
        const response = await fetch(`${API_BASE_URL}/api/news`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(newsData)
        });
        if (!response.ok) throw new Error('Failed to create news');
        return response.json();
    }
};

// Donations API
export const donationsApi = {
    create: async (donationData: {
        userId: string;
        amount: number;
        currency?: string;
        projectId?: string;
        status?: string;
    }) => {
        const response = await fetch(`${API_BASE_URL}/api/donations`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(donationData)
        });
        if (!response.ok) throw new Error('Failed to create donation');
        return response.json();
    },

    getAll: async () => {
        const response = await fetch(`${API_BASE_URL}/api/donations`);
        if (!response.ok) throw new Error('Failed to fetch donations');
        return response.json();
    },

    getDonorInfo: async (userId: string) => {
        const response = await fetch(`${API_BASE_URL}/api/donations/donor/${userId}`);
        if (!response.ok) throw new Error('Failed to fetch donor info');
        return response.json();
    },

    distributeToProjects: async (userId: string, donationAmount: number, projectIds: string[]) => {
        const response = await fetch(`${API_BASE_URL}/api/donations/donor/${userId}/distribute`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ donationAmount, projectIds })
        });
        if (!response.ok) throw new Error('Failed to distribute donation');
        return response.json();
    }
};

// Voting API
export const votingApi = {
    getAll: async () => {
        const response = await fetch(`${API_BASE_URL}/api/voting`);
        if (!response.ok) throw new Error('Failed to fetch voting');
        return response.json();
    },

    getById: async (id: string) => {
        const response = await fetch(`${API_BASE_URL}/api/voting/${id}`);
        if (!response.ok) throw new Error('Failed to fetch voting');
        return response.json();
    },

    vote: async (votingId: string, userId: string, vote: 'up' | 'down') => {
        const response = await fetch(`${API_BASE_URL}/api/voting/${votingId}/vote?user_id=${userId}&vote=${vote}`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' }
        });
        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.detail || 'Failed to submit vote');
        }
        return response.json();
    }
};

// Reports API
export const reportsApi = {
    create: async (reportData: {
        userId?: string;
        description: string;
        location?: string;
        photos?: string[];
        videos?: string[];
    }) => {
        const response = await fetch(`${API_BASE_URL}/api/reports`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(reportData)
        });
        if (!response.ok) throw new Error('Failed to submit report');
        return response.json();
    },

    getAll: async () => {
        const response = await fetch(`${API_BASE_URL}/api/reports`);
        if (!response.ok) throw new Error('Failed to fetch reports');
        return response.json();
    }
};

// Projects API
export const projectsApi = {
    getAll: async () => {
        const response = await fetch(`${API_BASE_URL}/api/projects`);
        if (!response.ok) throw new Error('Failed to fetch projects');
        return response.json();
    },

    getById: async (id: string) => {
        const response = await fetch(`${API_BASE_URL}/api/projects/${id}`);
        if (!response.ok) throw new Error('Failed to fetch project');
        return response.json();
    },

    create: async (projectData: any) => {
        const response = await fetch(`${API_BASE_URL}/api/projects`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(projectData)
        });
        if (!response.ok) throw new Error('Failed to create project');
        return response.json();
    },

    update: async (id: string, updates: any) => {
        const response = await fetch(`${API_BASE_URL}/api/projects/${id}`, {
            method: 'PATCH',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(updates)
        });
        if (!response.ok) throw new Error('Failed to update project');
        return response.json();
    }
};

// Stats API
export const statsApi = {
    getAll: async () => {
        const response = await fetch(`${API_BASE_URL}/api/stats`);
        if (!response.ok) throw new Error('Failed to fetch stats');
        return response.json();
    }
};

// AQI API (with health risks)
export const aqiApi = {
    get: async (city: string = 'Tashkent', country: string = 'Uzbekistan') => {
        const response = await fetch(`${API_BASE_URL}/api/air-quality?city=${city}&country=${country}`);
        if (!response.ok) throw new Error('Failed to fetch AQI');
        return response.json();
    }
};

// Complaints AI API
const COMPLAINTS_API_URL = 'https://complaints-service-242593050011.us-central1.run.app';

export const complaintsApi = {
    analyzeComplaint: async (formData: FormData) => {
        const response = await fetch(`${COMPLAINTS_API_URL}/analyze-complaint`, {
            method: 'POST',
            body: formData  // multipart/form-data with image and description
        });
        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.detail || 'Failed to analyze complaint');
        }
        return response.json();
    },

    getComplaint: async (id: string) => {
        const response = await fetch(`${COMPLAINTS_API_URL}/complaints/${id}`);
        if (!response.ok) throw new Error('Failed to fetch complaint');
        return response.json();
    },

    getViolations: async () => {
        const response = await fetch(`${COMPLAINTS_API_URL}/violations`);
        if (!response.ok) throw new Error('Failed to fetch violations');
        return response.json();
    },

    getComplaintsBatch: async (complaintIds: string[]) => {
        const response = await fetch(`${COMPLAINTS_API_URL}/complaints/batch`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(complaintIds)
        });
        if (!response.ok) throw new Error('Failed to fetch complaints');
        return response.json();
    }
};

