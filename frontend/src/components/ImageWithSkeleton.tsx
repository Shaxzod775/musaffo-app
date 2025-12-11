import React, { useState } from 'react';

interface Props {
    src: string;
    alt: string;
    className?: string;
}

const ImageWithSkeleton: React.FC<Props> = ({ src, alt, className = '' }) => {
    const [isLoaded, setIsLoaded] = useState(false);
    const [hasError, setHasError] = useState(false);

    return (
        <div className={`relative ${className}`}>
            {/* Skeleton */}
            {!isLoaded && !hasError && (
                <div className="absolute inset-0 bg-gradient-to-r from-[#E5E7EB] via-[#F3F4F6] to-[#E5E7EB] animate-shimmer bg-[length:200%_100%]" />
            )}

            {/* Actual Image */}
            <img
                src={src}
                alt={alt}
                className={`${className} transition-opacity duration-300 ${isLoaded ? 'opacity-100' : 'opacity-0'}`}
                onLoad={() => setIsLoaded(true)}
                onError={() => {
                    setHasError(true);
                    setIsLoaded(true);
                }}
            />

            {/* Error Fallback */}
            {hasError && (
                <div className="absolute inset-0 bg-[#F3F4F6] flex items-center justify-center">
                    <svg className="w-8 h-8 text-[#9CA3AF]" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z" />
                    </svg>
                </div>
            )}
        </div>
    );
};

export default ImageWithSkeleton;
