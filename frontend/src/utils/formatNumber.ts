// Format number with spaces every 3 digits
// Example: 10000 -> 10 000
export const formatNumber = (num: number | string): string => {
    const numStr = String(num);
    return numStr.replace(/\B(?=(\d{3})+(?!\d))/g, ' ');
};

// Format currency (add UZS suffix)
export const formatCurrency = (num: number | string): string => {
    return `${formatNumber(num)} UZS`;
};
