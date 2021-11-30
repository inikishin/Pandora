import { format } from 'date-fns';

const formatDateTime = (date) => format(new Date(date), 'dd MMM yyyy | HH:mm');

export default formatDateTime;
