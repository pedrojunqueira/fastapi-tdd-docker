import { useAuth } from "../context/AuthContext";

export function LoginPage() {
  const { login, isAuthenticated, isLoading, user, registerUser } = useAuth();

  if (isLoading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="flex flex-col items-center text-gray-500">
          <div className="w-10 h-10 border-4 border-gray-300 border-t-primary rounded-full animate-spin mb-4"></div>
          <p>Loading...</p>
        </div>
      </div>
    );
  }

  // User is authenticated with Azure but not registered in our app
  if (isAuthenticated && !user) {
    return (
      <div className="flex items-center justify-center min-h-screen pt-0">
        <div className="text-center bg-white p-12 rounded-lg shadow-lg max-w-md w-full">
          <h1 className="text-2xl font-bold text-primary mb-4">
            Welcome to Summaries
          </h1>
          <p className="text-gray-500 mb-2">
            You're signed in with Azure AD, but not registered in this app yet.
          </p>
          <p className="text-gray-500 mb-6">
            Click below to complete your registration.
          </p>
          <button
            onClick={registerUser}
            className="px-6 py-2 bg-primary text-white font-medium rounded-lg hover:bg-primary-hover transition-colors"
          >
            Complete Registration
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="flex items-center justify-center min-h-screen pt-0">
      <div className="text-center bg-white p-12 rounded-lg shadow-lg max-w-md w-full">
        <h1 className="text-2xl font-bold text-primary mb-4">Summaries App</h1>
        <p className="text-gray-500 mb-6">
          Manage your URL summaries with ease
        </p>
        <button
          onClick={login}
          className="px-6 py-2 bg-primary text-white font-medium rounded-lg hover:bg-primary-hover transition-colors"
        >
          Sign in with Microsoft
        </button>
      </div>
    </div>
  );
}
