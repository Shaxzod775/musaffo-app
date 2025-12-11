import React, { useState, useEffect } from 'react';
import { X, ThumbsUp, ThumbsDown, ChevronDown, ChevronUp, User } from 'lucide-react';
import { FundProject, UserState } from '../types';
import { useLanguage } from '../context/LanguageContext';

interface Props {
    initiative: FundProject;
    user: UserState;
    onClose: () => void;
    onVote: (id: string, type: 'up' | 'down') => void;
}

const VOTES_STORAGE_KEY = 'musaffo_votes';

const InitiativeDetail: React.FC<Props> = ({ initiative, user, onClose, onVote }) => {
    const { t } = useLanguage();
    const [showVoters, setShowVoters] = useState(false);
    const [userVote, setUserVote] = useState<'up' | 'down' | null>(null);

    // Block body scroll when modal is open
    useEffect(() => {
        document.body.style.overflow = 'hidden';
        return () => {
            document.body.style.overflow = 'unset';
        };
    }, []);

    // Load user's vote from localStorage
    useEffect(() => {
        const votes = JSON.parse(localStorage.getItem(VOTES_STORAGE_KEY) || '{}');
        if (votes[initiative.id]) {
            setUserVote(votes[initiative.id]);
        }
    }, [initiative.id]);

    const handleVote = (type: 'up' | 'down') => {
        // Save vote to localStorage
        const votes = JSON.parse(localStorage.getItem(VOTES_STORAGE_KEY) || '{}');
        votes[initiative.id] = type;
        localStorage.setItem(VOTES_STORAGE_KEY, JSON.stringify(votes));

        setUserVote(type);
        onVote(initiative.id, type);
    };

    // Mock voters data
    const mockVoters = [
        { name: 'Aziz R.', phone: '+998 90 *** ** 12', vote: 'up' },
        { name: 'Malika K.', phone: '+998 93 *** ** 45', vote: 'up' },
        { name: 'Javlon B.', phone: '+998 97 *** ** 99', vote: 'down' },
        { name: 'Sardor T.', phone: '+998 99 *** ** 01', vote: 'up' },
        { name: 'Bekzod A.', phone: '+998 91 *** ** 33', vote: 'up' },
        { name: 'Dilnoza M.', phone: '+998 94 *** ** 77', vote: 'down' },
    ];

    const votesFor = initiative.votesFor || 0;
    const votesAgainst = initiative.votesAgainst || 0;
    const total = votesFor + votesAgainst;
    const percentFor = total > 0 ? Math.round((votesFor / total) * 100) : 50;

    return (
        <div className="fixed inset-0 z-[100] bg-white flex flex-col animate-slide-up">
            {/* Header */}
            <div className="relative h-64 w-full shrink-0">
                <img
                    src={initiative.image}
                    className="w-full h-full object-cover"
                    alt={initiative.title}
                />
                <div className="absolute inset-0 bg-gradient-to-b from-black/60 to-transparent"></div>
                <button
                    onClick={onClose}
                    className="absolute top-4 right-4 bg-black/20 backdrop-blur p-2 rounded-full text-white hover:bg-black/40 transition-colors"
                >
                    <X size={24} />
                </button>
                <div className="absolute bottom-6 left-6 right-6 text-white">
                    <span className="bg-[#F59E0B] text-white px-2 py-1 rounded-md text-[10px] font-bold uppercase mb-2 inline-block">
                        {t('fund_status_voting')}
                    </span>
                    <h1 className="text-2xl font-bold leading-tight">{initiative.titleKey ? t(initiative.titleKey) : initiative.title}</h1>
                </div>
            </div>

            {/* Content */}
            <div className="flex-1 overflow-y-auto p-6">
                {/* Voting Stats with Animation */}
                <div className="w-full bg-[#F3F4F6] rounded-full h-12 flex relative overflow-hidden mb-6 shadow-inner">
                    <div
                        className="bg-[#27AE60] h-full flex items-center pl-4 text-xs text-white font-bold transition-all duration-700 ease-out"
                        style={{ width: `${percentFor}%` }}
                    >
                        <ThumbsUp size={16} className="mr-2" /> {votesFor}
                    </div>
                    <div className="bg-[#EB5757] h-full flex items-center justify-end pr-4 text-xs text-white font-bold flex-1 transition-all duration-700 ease-out">
                        {votesAgainst} <ThumbsDown size={16} className="ml-2" />
                    </div>
                </div>

                <div className="mb-8">
                    <h3 className="font-bold text-[#1F2937] mb-3">{t('initiative_about_title')}</h3>
                    <p className="text-sm text-[#4B5563] leading-relaxed">{initiative.descKey ? t(initiative.descKey) : initiative.description}</p>
                    <p className="text-sm text-[#4B5563] leading-relaxed mt-4">
                        {t('initiative_about_description')}
                    </p>
                </div>

                {/* Transparency List */}
                <div className="border-t border-[#E5E7EB] pt-4">
                    <button
                        onClick={() => setShowVoters(!showVoters)}
                        className="w-full flex justify-between items-center py-2 group"
                    >
                        <div className="flex items-center gap-2">
                            <User size={20} className="text-[#9CA3AF]" />
                            <span className="font-bold text-[#1F2937]">{t('voters_title')}</span>
                        </div>
                        {showVoters ? <ChevronUp size={20} className="text-[#9CA3AF]" /> : <ChevronDown size={20} className="text-[#9CA3AF]" />}
                    </button>

                    {showVoters && (
                        <div className="space-y-3 mt-4 animate-fade-in">
                            {mockVoters.map((voter, i) => (
                                <div key={i} className="flex justify-between items-center text-sm bg-[#F9FAFB] p-3 rounded-xl">
                                    <div className="flex items-center gap-3">
                                        <div className={`w-2 h-2 rounded-full ${voter.vote === 'up' ? 'bg-[#27AE60]' : 'bg-[#EB5757]'}`} />
                                        <span className="font-bold text-[#1F2937]">{voter.name}</span>
                                    </div>
                                    <span className="text-[#9CA3AF] font-mono text-xs">{voter.phone}</span>
                                </div>
                            ))}
                            <div className="text-center text-xs text-[#9CA3AF] pt-2">
                                {t('initiative_voters_others', { count: '1200' })}
                            </div>
                        </div>
                    )}
                </div>
            </div>

            {/* Footer Voting Actions */}
            <div className="p-4 border-t border-[#E5E7EB] bg-white pb-safe">
                {!user.isContributor ? (
                    <div className="bg-[#F59E0B]/10 border border-[#F59E0B] p-3 rounded-xl text-[#F59E0B] text-xs text-center">
                        <p className="font-bold">{t('vote_locked_msg')}</p>
                    </div>
                ) : (
                    <div className="flex gap-3">
                        <button
                            onClick={() => handleVote('up')}
                            disabled={userVote !== null}
                            className={`flex-1 py-3.5 rounded-xl font-bold flex items-center justify-center gap-2 transition-all ${userVote === 'up'
                                    ? 'bg-[#27AE60] text-white shadow-lg scale-95'
                                    : userVote === null
                                        ? 'bg-[#27AE60]/10 text-[#27AE60] hover:bg-[#27AE60] hover:text-white active:scale-95'
                                        : 'bg-[#E5E7EB] text-[#9CA3AF] cursor-not-allowed'
                                }`}
                        >
                            <ThumbsUp size={20} /> {t('vote_btn_support')}
                        </button>
                        <button
                            onClick={() => handleVote('down')}
                            disabled={userVote !== null}
                            className={`flex-1 py-3.5 rounded-xl font-bold flex items-center justify-center gap-2 transition-all ${userVote === 'down'
                                    ? 'bg-[#EB5757] text-white shadow-lg scale-95'
                                    : userVote === null
                                        ? 'bg-[#EB5757]/10 text-[#EB5757] hover:bg-[#EB5757] hover:text-white active:scale-95'
                                        : 'bg-[#E5E7EB] text-[#9CA3AF] cursor-not-allowed'
                                }`}
                        >
                            <ThumbsDown size={20} /> {t('vote_btn_against')}
                        </button>
                    </div>
                )}
            </div>
        </div>
    );
};

export default InitiativeDetail;
