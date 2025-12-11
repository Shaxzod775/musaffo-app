import React, { useState, useEffect, useRef } from 'react';

interface CasinoDigitProps {
    digit: string;
    delay: number;
    duration: number;
    shouldAnimate: boolean;
}

const CasinoDigit: React.FC<CasinoDigitProps> = ({ digit, delay, duration, shouldAnimate }) => {
    const [currentDigit, setCurrentDigit] = useState(digit);
    const [isAnimating, setIsAnimating] = useState(false);
    const prevDigitRef = useRef(digit);

    useEffect(() => {
        if (!shouldAnimate) {
            setCurrentDigit(digit);
            return;
        }

        // Check if digit changed
        if (prevDigitRef.current !== digit) {
            setIsAnimating(true);

            const startTime = Date.now() + delay;
            const endTime = startTime + duration;

            const animate = () => {
                const now = Date.now();

                if (now < startTime) {
                    requestAnimationFrame(animate);
                    return;
                }

                if (now < endTime) {
                    // Roll through digits
                    setCurrentDigit(Math.floor(Math.random() * 10).toString());
                    requestAnimationFrame(animate);
                } else {
                    // Done - show final digit
                    setCurrentDigit(digit);
                    setIsAnimating(false);
                    prevDigitRef.current = digit;
                }
            };

            requestAnimationFrame(animate);
        } else {
            setCurrentDigit(digit);
        }
    }, [digit, delay, duration, shouldAnimate]);

    // Initial animation on mount
    useEffect(() => {
        if (shouldAnimate) {
            setIsAnimating(true);
            const startTime = Date.now() + delay;
            const endTime = startTime + duration;

            const animate = () => {
                const now = Date.now();

                if (now < startTime) {
                    requestAnimationFrame(animate);
                    return;
                }

                if (now < endTime) {
                    setCurrentDigit(Math.floor(Math.random() * 10).toString());
                    requestAnimationFrame(animate);
                } else {
                    setCurrentDigit(digit);
                    setIsAnimating(false);
                    prevDigitRef.current = digit;
                }
            };

            requestAnimationFrame(animate);
        }
    }, []); // Only on mount

    return (
        <span
            className={`inline-block transition-all duration-100 overflow-hidden ${isAnimating ? 'blur-[0.5px]' : ''}`}
            style={{
                transform: isAnimating ? 'translateY(-2px)' : 'translateY(0)',
            }}
        >
            <span className={isAnimating ? '' : 'animate-roll-up'}>
                {currentDigit}
            </span>
        </span>
    );
};

interface CasinoCounterProps {
    value: number;
    className?: string;
    isLoading?: boolean;
}

const CasinoCounter: React.FC<CasinoCounterProps> = ({
    value,
    className = '',
    isLoading = false
}) => {
    const [mounted, setMounted] = useState(false);
    const [animationKey, setAnimationKey] = useState(0);
    const prevValueRef = useRef(value);

    useEffect(() => {
        setMounted(true);
    }, []);

    // Trigger re-animation when value changes
    useEffect(() => {
        if (prevValueRef.current !== value && mounted) {
            setAnimationKey(prev => prev + 1);
            prevValueRef.current = value;
        }
    }, [value, mounted]);

    if (isLoading || !mounted) {
        return <span className={className}>...</span>;
    }

    // Format number with spaces: 1 400 000 000
    const formattedValue = value.toString().replace(/\B(?=(\d{3})+(?!\d))/g, ' ');
    const parts = formattedValue.split('');

    return (
        <span className={className} key={animationKey}>
            {parts.map((char, index) => {
                if (char === ' ') {
                    return <span key={`space-${index}`}>&nbsp;</span>;
                }

                return (
                    <CasinoDigit
                        key={`digit-${index}-${animationKey}`}
                        digit={char}
                        delay={index * 30}
                        duration={600 + Math.random() * 300}
                        shouldAnimate={true}
                    />
                );
            })}
        </span>
    );
};

export default CasinoCounter;
