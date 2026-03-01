/**
 * Environment configuration management
 * Validates and provides type-safe access to environment variables
 */

export const ENV = {
  development: 'development',
  production: 'production',
  test: 'test',
} as const;

export type Environment = typeof ENV[keyof typeof ENV];

/**
 * Get environment variable with optional default
 */
function getEnv(key: string, defaultValue?: string): string {
  const value = typeof process !== 'undefined' 
    ? process.env[key] 
    : (import.meta as any).env?.[key];
  
  if (value === undefined && defaultValue === undefined) {
    throw new Error(`Missing required environment variable: ${key}`);
  }
  
  return value ?? defaultValue!;
}

/**
 * Get boolean environment variable
 */
function getBoolEnv(key: string, defaultValue = false): boolean {
  const value = typeof process !== 'undefined'
    ? process.env[key]
    : (import.meta as any).env?.[key];
  
  if (value === undefined) return defaultValue;
  return value === 'true' || value === '1';
}

/**
 * Get number environment variable
 */
function getNumberEnv(key: string, defaultValue?: number): number {
  const value = typeof process !== 'undefined'
    ? process.env[key]
    : (import.meta as any).env?.[key];
  
  if (value === undefined) {
    if (defaultValue === undefined) {
      throw new Error(`Missing required environment variable: ${key}`);
    }
    return defaultValue;
  }
  
  const parsed = parseInt(value, 10);
  if (isNaN(parsed)) {
    throw new Error(`Invalid number for environment variable ${key}: ${value}`);
  }
  return parsed;
}

/**
 * Application configuration
 */
export const config = {
  env: getEnv('NODE_ENV', ENV.development) as Environment,
  isDevelopment: getEnv('NODE_ENV', ENV.development) === ENV.development,
  isProduction: getEnv('NODE_ENV', ENV.development) === ENV.production,
  isTest: getEnv('NODE_ENV', ENV.development) === ENV.test,
  
  // Frontend config
  frontend: {
    appTitle: getEnv('VITE_APP_TITLE', 'TicTacToe'),
    apiUrl: getEnv('VITE_API_URL', 'http://localhost:3000'),
    wsUrl: getEnv('VITE_WS_URL', 'ws://localhost:3000'),
    enableDebug: getBoolEnv('VITE_ENABLE_DEBUG', true),
  },
  
  // Backend config
  backend: {
    port: getNumberEnv('PORT', 3000),
    host: getEnv('HOST', '0.0.0.0'),
    corsOrigin: getEnv('CORS_ORIGIN', 'http://localhost:5173'),
  },
  
  // Database config
  database: {
    url: getEnv('DATABASE_URL', ''),
  },
  
  // Redis config
  redis: {
    url: getEnv('REDIS_URL', 'redis://localhost:6379'),
  },
  
  // Logging
  logging: {
    level: getEnv('LOG_LEVEL', 'info'),
  },
  
  // Security
  security: {
    jwtSecret: getEnv('JWT_SECRET', 'dev-secret-change-me'),
    sessionSecret: getEnv('SESSION_SECRET', 'dev-session-secret-change-me'),
  },
};

/**
 * Validate required production environment variables
 */
export function validateProductionEnv(): void {
  if (!config.isProduction) return;
  
  const requiredVars = [
    'JWT_SECRET',
    'SESSION_SECRET',
  ];
  
  const missing = requiredVars.filter(key => {
    const value = typeof process !== 'undefined'
      ? process.env[key]
      : (import.meta as any).env?.[key];
    return !value || value.includes('change-me') || value.includes('dev-');
  });
  
  if (missing.length > 0) {
    throw new Error(
      `Missing or invalid production environment variables: ${missing.join(', ')}`
    );
  }
}

export default config;