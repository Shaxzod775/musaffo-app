import React, { useState, useEffect } from 'react';
import { CheckCircle, AlertTriangle, ThumbsUp, ThumbsDown, ChevronDown, ChevronUp, FileText, Camera, Video, Trash2, Send, CheckCircle2, X, Loader2, ImagePlus, Clock, XCircle } from 'lucide-react';
import { FundProject, UserState, Tab } from '../types';
import { useLanguage } from '../context/LanguageContext';
import { complaintsApi } from '../services/api';

const COMPLAINTS_STORAGE_KEY = 'musaffo_my_complaints';

interface Complaint {
    id: string;
    status: 'pending' | 'confirmed' | 'rejected';
    created_at: string;
    analysis?: {
        violation_name?: string;
        violation_detected?: boolean;
    };
}

interface Props {
    user: UserState;
    projects: FundProject[];
    setActiveTab: (tab: Tab) => void;
    onInitiativeClick: (initiative: FundProject) => void;
    onVote: (projectId: string, voteType: 'for' | 'against') => void;
}

const CommunityView: React.FC<Props> = ({ user, projects, setActiveTab, onInitiativeClick, onVote }) => {
    const { t } = useLanguage();
    const [mode, setMode] = useState<'vote' | 'report'>('vote');
    const [expandedProject, setExpandedProject] = useState<string | null>(null);

    // Report state
    const [reportStep, setReportStep] = useState(0);
    const [complaintText, setComplaintText] = useState('');
    const [violationAddress, setViolationAddress] = useState('');
    const [selectedPhotos, setSelectedPhotos] = useState<File[]>([]);
    const [selectedVideos, setSelectedVideos] = useState<File[]>([]);
    const [photoPreview, setPhotoPreview] = useState<string[]>([]);
    const [isSubmitting, setIsSubmitting] = useState(false);
    const [analysisResult, setAnalysisResult] = useState<any>(null);

    // My complaints state
    const [myComplaints, setMyComplaints] = useState<Complaint[]>([]);
    const [complaintsLoading, setComplaintsLoading] = useState(false);

    // Load votes from localStorage
    const [userVotes, setUserVotes] = useState<Record<string, 'up' | 'down'>>({});

    useEffect(() => {
        const VOTES_STORAGE_KEY = 'musaffo_votes';
        const votes = JSON.parse(localStorage.getItem(VOTES_STORAGE_KEY) || '{}');
        setUserVotes(votes);
    }, []);

    // Load user's complaints from localStorage and fetch their status
    useEffect(() => {
        const fetchMyComplaints = async () => {
            const complaintIds: string[] = JSON.parse(localStorage.getItem(COMPLAINTS_STORAGE_KEY) || '[]');
            if (complaintIds.length === 0) return;

            setComplaintsLoading(true);
            try {
                const response = await complaintsApi.getComplaintsBatch(complaintIds);
                setMyComplaints(response.complaints || []);
            } catch (error) {
                console.error('Error fetching complaints:', error);
            } finally {
                setComplaintsLoading(false);
            }
        };

        fetchMyComplaints();
    }, []);

    const Header = ({ title, subtitle }: { title: string, subtitle?: string }) => (
        <div className="bg-main-gradient pt-10 pb-16 px-6 rounded-b-[30px] shadow-lg shadow-[#40A7E3]/20 relative overflow-hidden">
            <div className="absolute inset-0 opacity-10" style={{
                backgroundImage: `url("data:image/svg+xml,%3Csvg width='60' height='60' viewBox='0 0 60 60' xmlns='http://www.w3.org/2000/svg'%3E%3Cpath d='M30 0L60 30L30 60L0 30z' fill='%23ffffff'/%3E%3C/svg%3E")`
            }} />
            <div className="relative z-10 text-white">
                <h1 className="text-3xl font-bold tracking-tight">{title}</h1>
                {subtitle && <p className="text-sm opacity-90 font-medium">{subtitle}</p>}
            </div>
        </div>
    );

    const handlePhotoChange = (e: React.ChangeEvent<HTMLInputElement>) => {
        const files = Array.from(e.target.files || []);
        if (selectedPhotos.length + files.length > 10) {
            alert(t('report_max_photos'));
            return;
        }
        setSelectedPhotos(prev => [...prev, ...files]);
    };

    const handleVideoChange = (e: React.ChangeEvent<HTMLInputElement>) => {
        const files = Array.from(e.target.files || []);
        if (selectedVideos.length + files.length > 2) {
            alert(t('report_max_videos'));
            return;
        }
        setSelectedVideos(prev => [...prev, ...files]);
    };

    const removePhoto = (index: number) => {
        setSelectedPhotos(prev => prev.filter((_, i) => i !== index));
    };

    const removeVideo = (index: number) => {
        setSelectedVideos(prev => prev.filter((_, i) => i !== index));
    };

    const handleSubmitComplaint = async () => {
        // Validate minimum 3 photos
        if (selectedPhotos.length < 3) {
            alert(t('report_min_photos') || 'Пожалуйста, загрузите минимум 3 фото');
            return;
        }

        if (!complaintText.trim()) {
            alert(t('report_need_description') || 'Пожалуйста, добавьте описание нарушения');
            return;
        }

        if (!violationAddress.trim()) {
            alert(t('report_need_address') || 'Пожалуйста, укажите адрес нарушения');
            return;
        }

        setIsSubmitting(true);

        try {
            // Create FormData with all photos, description and address
            const formData = new FormData();
            // Append all photos
            selectedPhotos.forEach((photo) => {
                formData.append('images', photo);
            });
            formData.append('description', complaintText);
            formData.append('address', violationAddress);

            // Call AI API
            const result = await complaintsApi.analyzeComplaint(formData);

            console.log('AI Analysis Result:', result);

            // Store analysis result
            setAnalysisResult(result);

            // Save complaint_id to localStorage
            if (result.complaint_id) {
                const existingIds: string[] = JSON.parse(localStorage.getItem(COMPLAINTS_STORAGE_KEY) || '[]');
                if (!existingIds.includes(result.complaint_id)) {
                    existingIds.unshift(result.complaint_id); // Add to beginning
                    localStorage.setItem(COMPLAINTS_STORAGE_KEY, JSON.stringify(existingIds));
                }
                // Update myComplaints state
                setMyComplaints(prev => [{
                    id: result.complaint_id,
                    status: 'pending',
                    created_at: new Date().toISOString(),
                    analysis: {
                        violation_name: result.violation_name,
                        violation_detected: result.violation_detected
                    }
                }, ...prev]);
            }

            // Show success
            setReportStep(1);
        } catch (error) {
            console.error('Error analyzing complaint:', error);
            alert('Ошибка при анализе жалобы. Попробуйте позже.');
        } finally {
            setIsSubmitting(false);
        }
    };

    const resetForm = () => {
        setReportStep(0);
        setComplaintText('');
        setViolationAddress('');
        setSelectedPhotos([]);
        setSelectedVideos([]);
        setAnalysisResult(null);
    };

    const toggleTransparency = (id: string) => {
        if (expandedProject === id) setExpandedProject(null);
        else setExpandedProject(id);
    };

    // Mock voters data
    const mockVoters = [
        { name: 'Aziz R.', phone: '+998 90 *** ** 12', vote: 'up' },
        { name: 'Malika K.', phone: '+998 93 *** ** 45', vote: 'up' },
        { name: 'Javlon B.', phone: '+998 97 *** ** 99', vote: 'down' },
        { name: 'Sardor T.', phone: '+998 99 *** ** 01', vote: 'up' },
    ];

    return (
        <div className="pb-32 animate-fade-in bg-[#F3F4F6] min-h-screen">
            <Header title={t('community_title')} subtitle={t('community_subtitle')} />

            <div className="px-5 -mt-8 relative z-20">
                {/* Toggle */}
                <div className="bg-white p-1 rounded-2xl shadow-soft flex mb-6">
                    <button
                        onClick={() => setMode('vote')}
                        className={`flex-1 py-3 rounded-xl text-xs font-bold transition-all ${mode === 'vote' ? 'bg-[#40A7E3] text-white shadow-md' : 'text-[#9CA3AF]'}`}
                    >
                        {t('tab_vote')}
                    </button>
                    <button
                        onClick={() => setMode('report')}
                        className={`flex-1 py-3 rounded-xl text-xs font-bold transition-all ${mode === 'report' ? 'bg-[#EB5757] text-white shadow-md' : 'text-[#9CA3AF]'}`}
                    >
                        {t('tab_report')}
                    </button>
                </div>

                {mode === 'vote' ? (
                    <div className="space-y-6">
                        {/* User Status Card */}
                        <div className="bg-gradient-to-r from-[#1F2937] to-[#374151] p-5 card-radius text-white flex items-center justify-between animate-fade-in">
                            <div>
                                <p className="text-[10px] uppercase font-bold opacity-70">{t('user_status_label')}</p>
                                <p className="font-bold text-lg animate-counter">{user.isContributor ? t('user_status_donor') : t('user_status_guest')}</p>
                            </div>
                            <div className="bg-white/10 p-2 rounded-lg">
                                {user.isContributor ? <CheckCircle className="text-[#27AE60]" /> : <AlertTriangle className="text-[#F59E0B]" />}
                            </div>
                        </div>
                        {!user.isContributor && (
                            <div className="bg-[#F59E0B]/10 border border-[#F59E0B] p-4 rounded-xl text-[#F59E0B] text-xs">
                                <p className="font-bold flex items-center gap-2"><AlertTriangle size={14} /> {t('vote_locked_msg')}</p>
                                <button onClick={() => { setActiveTab('fund'); }} className="mt-2 underline font-bold">{t('btn_contribute')}</button>
                            </div>
                        )}

                        {/* Voting Projects */}
                        <h3 className="font-bold text-[#1F2937]">{t('vote_cta_title')}</h3>
                        {projects.filter(p => p.status === 'voting').map(p => (
                            <div key={p.id} onClick={() => onInitiativeClick(p)} className="bg-white p-5 card-radius shadow-soft cursor-pointer active:scale-[0.98] transition-transform">
                                <div className="flex gap-4 mb-4">
                                    <img src={p.image} className="w-16 h-16 rounded-xl object-cover" alt={p.title} />
                                    <div>
                                        <h4 className="font-bold text-sm">{p.titleKey ? t(p.titleKey) : p.title}</h4>
                                        <p className="text-xs text-[#4B5563] mt-1">{p.descKey ? t(p.descKey) : p.description}</p>
                                    </div>
                                </div>

                                <div className="w-full bg-[#F3F4F6] rounded-full h-8 flex relative overflow-hidden">
                                    <div className="bg-[#27AE60] h-full flex items-center pl-3 text-[10px] text-white font-bold transition-all animate-progress-bar" style={{ width: `${Math.round(((p.votesFor || 0) / ((p.votesFor || 0) + (p.votesAgainst || 1))) * 100)}%` }}>
                                        <span className="animate-counter">{p.votesFor}</span>
                                    </div>
                                    <div className="bg-[#EB5757] h-full flex items-center justify-end pr-3 text-[10px] text-white font-bold flex-1">
                                        <span className="animate-counter">{p.votesAgainst}</span>
                                    </div>
                                </div>

                                <div className="flex gap-3 mt-4">
                                    <button
                                        disabled={!user.isContributor || userVotes[p.id]}
                                        onClick={(e) => {
                                            e.stopPropagation();
                                            onVote(p.id, 'for');
                                            const VOTES_STORAGE_KEY = 'musaffo_votes';
                                            const votes = JSON.parse(localStorage.getItem(VOTES_STORAGE_KEY) || '{}');
                                            votes[p.id] = 'up';
                                            localStorage.setItem(VOTES_STORAGE_KEY, JSON.stringify(votes));
                                            setUserVotes(votes);
                                        }}
                                        className={`flex-1 py-3 rounded-xl text-xs font-bold flex items-center justify-center gap-2 transition-all ${userVotes[p.id] === 'up'
                                            ? 'bg-[#27AE60] text-white shadow-lg scale-95'
                                            : 'bg-[#27AE60]/10 text-[#27AE60] hover:bg-[#27AE60] hover:text-white disabled:opacity-50'
                                            }`}>
                                        <ThumbsUp size={16} /> {t('vote_btn_support')}
                                    </button>
                                    <button
                                        disabled={!user.isContributor || userVotes[p.id]}
                                        onClick={(e) => {
                                            e.stopPropagation();
                                            onVote(p.id, 'against');
                                            const VOTES_STORAGE_KEY = 'musaffo_votes';
                                            const votes = JSON.parse(localStorage.getItem(VOTES_STORAGE_KEY) || '{}');
                                            votes[p.id] = 'down';
                                            localStorage.setItem(VOTES_STORAGE_KEY, JSON.stringify(votes));
                                            setUserVotes(votes);
                                        }}
                                        className={`flex-1 py-3 rounded-xl text-xs font-bold flex items-center justify-center gap-2 transition-all ${userVotes[p.id] === 'down'
                                            ? 'bg-[#EB5757] text-white shadow-lg scale-95'
                                            : 'bg-[#EB5757]/10 text-[#EB5757] hover:bg-[#EB5757] hover:text-white disabled:opacity-50'
                                            }`}>
                                        <ThumbsDown size={16} /> {t('vote_btn_against')}
                                    </button>
                                </div>

                                {/* Transparency List */}
                                <div className="mt-4 border-t border-[#F3F4F6] pt-2">
                                    <button
                                        onClick={(e) => {
                                            e.stopPropagation();
                                            toggleTransparency(p.id);
                                        }}
                                        className="w-full flex justify-between items-center text-[10px] font-bold text-[#9CA3AF] py-2"
                                    >
                                        <span>{t('voters_title')}</span>
                                        {expandedProject === p.id ? <ChevronUp size={14} /> : <ChevronDown size={14} />}
                                    </button>

                                    {expandedProject === p.id && (
                                        <div className="space-y-2 mt-2 animate-fade-in">
                                            {mockVoters.map((voter, i) => (
                                                <div key={i} className="flex justify-between items-center text-[10px] bg-[#F9FAFB] p-2 rounded-lg">
                                                    <div className="flex items-center gap-2">
                                                        <div className={`w-1.5 h-1.5 rounded-full ${voter.vote === 'up' ? 'bg-[#27AE60]' : 'bg-[#EB5757]'}`} />
                                                        <span className="font-bold text-[#1F2937]">{voter.name}</span>
                                                    </div>
                                                    <span className="text-[#9CA3AF] font-mono">{voter.phone}</span>
                                                </div>
                                            ))}
                                            <div className="text-center text-[9px] text-[#9CA3AF] pt-1">
                                                +1200 {t('voters_others')}
                                            </div>
                                        </div>
                                    )}
                                </div>
                            </div>
                        ))}
                    </div>
                ) : (
                    <div className="space-y-4">
                        {reportStep === 0 ? (
                            <div className="bg-white card-radius p-6 shadow-soft space-y-5">
                                {/* Header */}
                                <div className="flex items-center gap-3">
                                    <div className="w-12 h-12 bg-[#EB5757]/10 rounded-full flex items-center justify-center text-[#EB5757]">
                                        <FileText size={24} />
                                    </div>
                                    <div>
                                        <h3 className="font-bold text-lg text-[#1F2937]">{t('report_title')}</h3>
                                        <p className="text-xs text-[#4B5563]">{t('report_desc')}</p>
                                    </div>
                                </div>

                                {/* Text Area */}
                                <textarea
                                    value={complaintText}
                                    onChange={(e) => setComplaintText(e.target.value)}
                                    placeholder={t('report_placeholder')}
                                    className="w-full h-32 p-4 border border-[#E5E7EB] rounded-xl text-sm resize-none focus:outline-none focus:ring-2 focus:ring-[#EB5757]/30 focus:border-[#EB5757]"
                                />

                                {/* Address Input */}
                                <div>
                                    <label className="block text-xs font-bold text-[#4B5563] mb-2">
                                        {t('report_address_label') || 'Адрес нарушения'} <span className="text-[#EB5757]">*</span>
                                    </label>
                                    <input
                                        type="text"
                                        value={violationAddress}
                                        onChange={(e) => setViolationAddress(e.target.value)}
                                        placeholder={t('report_address_placeholder') || 'Укажите адрес или ориентир (улица, район, здание)'}
                                        className="w-full p-4 border border-[#E5E7EB] rounded-xl text-sm focus:outline-none focus:ring-2 focus:ring-[#EB5757]/30 focus:border-[#EB5757]"
                                    />
                                </div>

                                {/* Photo Upload */}
                                <div>
                                    <label className="block text-xs font-bold text-[#4B5563] mb-2">
                                        {t('report_photos_label')} <span className="text-[#EB5757]">* {t('report_photos_requirement')}</span>
                                    </label>
                                    <input
                                        type="file"
                                        accept="image/*"
                                        multiple
                                        onChange={handlePhotoChange}
                                        className="hidden"
                                        id="photo-upload"
                                    />
                                    <label htmlFor="photo-upload" className={`flex items-center justify-center gap-2 w-full p-3 border-2 border-dashed rounded-xl text-xs font-bold cursor-pointer transition-colors ${selectedPhotos.length < 3 ? 'border-[#EB5757] text-[#EB5757] hover:bg-[#EB5757]/5' : 'border-[#27AE60] text-[#27AE60] hover:bg-[#27AE60]/5'}`}>
                                        <ImagePlus size={18} />
                                        {t('report_add_photos')} ({selectedPhotos.length}/10) {selectedPhotos.length < 3 && `— ${t('report_need_more_photos')} ${3 - selectedPhotos.length}`}
                                    </label>
                                    {selectedPhotos.length > 0 && (
                                        <div className="grid grid-cols-3 gap-2 mt-3">
                                            {selectedPhotos.map((photo, i) => (
                                                <div key={i} className="relative w-16 h-16 rounded-lg overflow-hidden bg-[#F3F4F6]">
                                                    <img
                                                        src={URL.createObjectURL(photo)}
                                                        alt={`Photo ${i + 1}`}
                                                        className="w-full h-full object-cover"
                                                    />
                                                    <button
                                                        onClick={() => removePhoto(i)}
                                                        className="absolute top-1 right-1 w-5 h-5 bg-[#EB5757] rounded-full flex items-center justify-center"
                                                    >
                                                        <X size={12} className="text-white" />
                                                    </button>
                                                </div>
                                            ))}
                                        </div>
                                    )}
                                </div>

                                {/* Video Upload */}
                                <div>
                                    <input
                                        type="file"
                                        accept="video/*"
                                        multiple
                                        onChange={handleVideoChange}
                                        className="hidden"
                                        id="video-upload"
                                    />
                                    <label htmlFor="video-upload" className="flex items-center justify-center gap-2 w-full p-3 border-2 border-dashed border-[#E5E7EB] rounded-xl text-[#9CA3AF] text-xs font-bold cursor-pointer hover:border-[#40A7E3] hover:text-[#40A7E3] transition-colors">
                                        <Video size={18} />
                                        {t('report_add_videos')} ({selectedVideos.length}/2)
                                    </label>
                                    {selectedVideos.length > 0 && (
                                        <div className="grid grid-cols-2 gap-2 mt-3">
                                            {selectedVideos.map((video, i) => (
                                                <div key={i} className="relative flex items-center gap-2 bg-[#F3F4F6] px-3 py-2 rounded-lg">
                                                    <Video size={16} className="text-[#4B5563]" />
                                                    <span className="text-xs text-[#1F2937] max-w-[100px] truncate">{video.name}</span>
                                                    <button
                                                        onClick={() => removeVideo(i)}
                                                        className="ml-auto p-15 bg-[#EB5757] rounded-full flex items-center justify-center"
                                                    >
                                                        <X size={12} className="text-white" />
                                                    </button>
                                                </div>
                                            ))}
                                        </div>
                                    )}
                                </div>

                                {/* Submit Button */}
                                <button
                                    onClick={handleSubmitComplaint}
                                    disabled={!complaintText.trim() || !violationAddress.trim() || selectedPhotos.length < 3 || isSubmitting}
                                    className="w-full bg-[#EB5757] text-white py-3.5 btn-radius font-bold shadow-lg shadow-[#EB5757]/30 active:scale-95 transition-transform disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-2"
                                >
                                    {isSubmitting ? (
                                        <>
                                            <Loader2 size={18} className="animate-spin" />
                                            {t('report_sending')}
                                        </>
                                    ) : (
                                        t('report_submit')
                                    )}
                                </button>
                            </div>
                        ) : (
                            <div className="bg-white card-radius p-6 shadow-soft animate-fade-in">
                                <div className="flex flex-col items-center text-center">
                                    <div className="w-16 h-16 bg-[#27AE60]/10 rounded-full flex items-center justify-center mb-4">
                                        <CheckCircle size={32} className="text-[#27AE60]" />
                                    </div>
                                    <h3 className="font-bold text-lg text-[#1F2937] mb-2">{t('report_success_title')}</h3>

                                    {/* AI Analysis Result */}
                                    {analysisResult && analysisResult.violation_detected ? (
                                        <div className="w-full space-y-4 mt-4">
                                            {/* Violation Type */}
                                            {analysisResult.violation_name && (
                                                <div className="bg-[#EB5757]/10 border border-[#EB5757]/20 rounded-xl p-4">
                                                    <p className="text-xs text-[#9CA3AF] mb-1">Обнаружено нарушение</p>
                                                    <p className="font-bold text-[#EB5757]">{analysisResult.violation_name}</p>
                                                </div>
                                            )}

                                            {/* Fine Estimate */}
                                            {analysisResult.fine_range && (
                                                <div className="bg-[#40A7E3]/10 border border-[#40A7E3]/20 rounded-xl p-4">
                                                    <p className="text-xs text-[#9CA3AF] mb-2">Оценка штрафа</p>
                                                    <div className="flex justify-between text-sm">
                                                        <span className="text-[#4B5563]">От:</span>
                                                        <span className="font-bold text-[#1F2937]">{(analysisResult.fine_range.min / 1000).toFixed(0)}K сум</span>
                                                    </div>
                                                    <div className="flex justify-between text-sm mt-1">
                                                        <span className="text-[#4B5563]">До:</span>
                                                        <span className="font-bold text-[#1F2937]">{(analysisResult.fine_range.max / 1000).toFixed(0)}K сум</span>
                                                    </div>
                                                </div>
                                            )}

                                            {/* Reward Estimate */}
                                            {analysisResult.reward_range && (
                                                <div className="bg-[#27AE60]/10 border border-[#27AE60]/20 rounded-xl p-4">
                                                    <p className="text-xs text-[#9CA3AF] mb-2">💰 Ваше вознаграждение (15%)</p>
                                                    <div className="flex justify-between text-sm">
                                                        <span className="text-[#4B5563]">От:</span>
                                                        <span className="font-bold text-[#27AE60]">{(analysisResult.reward_range.min / 1000).toFixed(0)}K сум</span>
                                                    </div>
                                                    <div className="flex justify-between text-sm mt-1">
                                                        <span className="text-[#4B5563]">До:</span>
                                                        <span className="font-bold text-[#27AE60]">{(analysisResult.reward_range.max / 1000).toFixed(0)}K сум</span>
                                                    </div>
                                                </div>
                                            )}

                                            {/* AI Raw Analysis */}
                                            {analysisResult.raw_analysis && (
                                                <div className="bg-[#F3F4F6] rounded-xl p-4 text-left">
                                                    <p className="text-xs text-[#9CA3AF] mb-2">Анализ ИИ:</p>
                                                    <p className="text-xs text-[#4B5563] whitespace-pre-line">{analysisResult.raw_analysis}</p>
                                                </div>
                                            )}
                                        </div>
                                    ) : (
                                        <p className="text-sm text-[#4B5563] mb-6">{t('report_success_desc')}</p>
                                    )}

                                    <button
                                        onClick={resetForm}
                                        className="w-full bg-[#F3F4F6] text-[#1F2937] py-3 rounded-xl font-bold text-sm hover:bg-[#E5E7EB] transition-colors mt-6"
                                    >
                                        {t('btn_report_again')}
                                    </button>
                                </div>
                            </div>
                        )}

                        {/* My Complaints Section */}
                        {myComplaints.length > 0 && (
                            <div className="bg-white card-radius p-5 shadow-soft mt-4">
                                <h3 className="font-bold text-[#1F2937] mb-4 flex items-center gap-2">
                                    <FileText size={18} className="text-[#40A7E3]" />
                                    Мои жалобы
                                </h3>
                                <div className="space-y-3">
                                    {complaintsLoading ? (
                                        <div className="flex justify-center py-4">
                                            <Loader2 size={24} className="animate-spin text-[#40A7E3]" />
                                        </div>
                                    ) : (
                                        myComplaints.map((complaint) => (
                                            <div key={complaint.id} className="bg-[#F9FAFB] rounded-xl p-4">
                                                <div className="flex items-start justify-between">
                                                    <div className="flex-1">
                                                        <p className="text-sm font-medium text-[#1F2937]">
                                                            {complaint.analysis?.violation_name || 'Жалоба отправлена'}
                                                        </p>
                                                        <p className="text-xs text-[#9CA3AF] mt-1">
                                                            {new Date(complaint.created_at).toLocaleDateString('ru-RU', {
                                                                day: 'numeric',
                                                                month: 'short',
                                                                year: 'numeric',
                                                                hour: '2-digit',
                                                                minute: '2-digit'
                                                            })}
                                                        </p>
                                                    </div>
                                                    <div className={`flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-bold ${complaint.status === 'pending'
                                                            ? 'bg-[#F59E0B]/10 text-[#F59E0B]'
                                                            : complaint.status === 'confirmed'
                                                                ? 'bg-[#27AE60]/10 text-[#27AE60]'
                                                                : 'bg-[#EB5757]/10 text-[#EB5757]'
                                                        }`}>
                                                        {complaint.status === 'pending' && <Clock size={12} />}
                                                        {complaint.status === 'confirmed' && <CheckCircle size={12} />}
                                                        {complaint.status === 'rejected' && <XCircle size={12} />}
                                                        {complaint.status === 'pending' && 'На рассмотрении'}
                                                        {complaint.status === 'confirmed' && 'Подтверждено'}
                                                        {complaint.status === 'rejected' && 'Отклонено'}
                                                    </div>
                                                </div>
                                            </div>
                                        ))
                                    )}
                                </div>
                            </div>
                        )}
                    </div>
                )}
            </div>
        </div>
    );
};

export default CommunityView;
