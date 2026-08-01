import algoliasearch from 'algoliasearch';

// Fallback to placeholders if environment variables are not yet provided by Fuzail's Firebase Extension
const APP_ID = process.env.ALGOLIA_APP_ID || 'APP_ID_PLACEHOLDER';
const SEARCH_API_KEY = process.env.ALGOLIA_SEARCH_API_KEY || 'SEARCH_KEY_PLACEHOLDER';

export const algoliaClient = algoliasearch(APP_ID, SEARCH_API_KEY);
export const hackathonIndex = algoliaClient.initIndex('hackathons');
