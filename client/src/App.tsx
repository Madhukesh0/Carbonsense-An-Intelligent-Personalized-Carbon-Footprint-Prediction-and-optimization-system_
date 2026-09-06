import { Toaster } from "@/components/ui/sonner";
import { TooltipProvider } from "@/components/ui/tooltip";
import { Route, Switch } from "wouter";
import ErrorBoundary from "./components/ErrorBoundary";
import AdminDashboard from "./pages/admin/Dashboard";
import ModelPreview from "./pages/admin/ModelPreview";
import AdminReports from "./pages/admin/Reports";
import AdminUsers from "./pages/admin/Users";
import Assistant from "./pages/Assistant";
import About from "./pages/About";
import Login from "./pages/auth/Login";
import ForgotPassword from "./pages/auth/ForgotPassword";
import Goals from "./pages/Goals";
import Register from "./pages/auth/Register";
import Baseline from "./pages/Baseline";
import ContributorsMap from "./pages/ContributorsMap";
import Dashboard from "./pages/Dashboard";
import Explore from "./pages/Explore";
import Forecast from "./pages/Forecast";
import History from "./pages/History";
import Insights from "./pages/Insights";
import NotFound from "./pages/NotFound";
import Organization from "./pages/Organization";
import Plan from "./pages/Plan";
import Profile from "./pages/Profile";
import Predict from "./pages/Predict";
import Privacy from "./pages/Privacy";
import Progress from "./pages/Progress";
import MyRecommendations from "./pages/MyRecommendations";
import ResultRecommendations from "./pages/ResultRecommendations";
import Recommendations from "./pages/Recommendations";
import Reminders from "./pages/Reminders";
import Quests from "./pages/Quests";
import Reports from "./pages/Reports";
import WhatIf from "./pages/WhatIf";
import { ThemeProvider } from "./contexts/ThemeContext";

function Router() {
  return <Switch>
    <Route path="/" component={Dashboard} />
    <Route path="/about" component={About} />
    <Route path="/activity" component={Progress} />
    <Route path="/assistant" component={Assistant} />
    <Route path="/docs" component={About} />
    <Route path="/login" component={Login} />
    <Route path="/register" component={Register} />
    <Route path="/forgot-password" component={ForgotPassword} />
    <Route path="/explore" component={Explore} />
    <Route path="/plan" component={Plan} />
    <Route path="/insights" component={Insights} />
    <Route path="/progress" component={Progress} />
    <Route path="/predict" component={Predict} />
    <Route path="/baseline" component={Baseline} />
    <Route path="/organization" component={Organization} />
    <Route path="/reminders" component={Reminders} />
    <Route path="/whatif" component={WhatIf} />
    <Route path="/history" component={History} />
    <Route path="/goals" component={Goals} />
    <Route path="/profile" component={Profile} />
    <Route path="/privacy" component={Privacy} />
    <Route path="/recommendations" component={Recommendations} />
    <Route path="/result-recommendations" component={ResultRecommendations} />
    <Route path="/my-recommendations" component={MyRecommendations} />
    <Route path="/quests" component={Quests} />
    <Route path="/contributors" component={ContributorsMap} />
    <Route path="/forecast" component={Forecast} />
    <Route path="/reports" component={Reports} />
    <Route path="/admin" component={AdminDashboard} />
    <Route path="/admin/users" component={AdminUsers} />
    <Route path="/admin/model-preview" component={ModelPreview} />
    <Route path="/admin/reports" component={AdminReports} />
    <Route component={NotFound} />
  </Switch>;
}

export default function App() {
  return <ErrorBoundary><ThemeProvider defaultTheme="light" switchable><TooltipProvider><Toaster /><Router /></TooltipProvider></ThemeProvider></ErrorBoundary>;
}
