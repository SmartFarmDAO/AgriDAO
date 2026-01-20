import { useTranslation } from '@/i18n/config';

export const useTranslate = () => {
  const { t } = useTranslation();
  
  return { t };
};
