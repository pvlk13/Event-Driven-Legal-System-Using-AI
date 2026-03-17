import logo from './logo.svg';
import './App.css';
import CaseDashboard from './CaseDashboard';
import { withAuthenticator } from '@aws-amplify/ui-react';
import '@aws-amplify/ui-react/styles.css';

function App() {
 return <CaseDashboard />;
}

export default withAuthenticator(App);
