import { createBrowserRouter } from "react-router-dom";
import { AppShell } from "../layouts/AppShell.jsx";
import { LiveDashboard } from "../pages/LiveDashboard.jsx";
import { UsageHistory } from "../pages/UsageHistory.jsx";
import { SmartControl } from "../pages/SmartControl.jsx";
import { Invoices } from "../pages/Invoices.jsx";
import { NotFound } from "../pages/NotFound.jsx";

export const router = createBrowserRouter([
  {
    element: <AppShell />,
    children: [
      { path: "/", element: <LiveDashboard /> },
      { path: "/analytics", element: <UsageHistory /> },
      { path: "/devices", element: <SmartControl /> },
      { path: "/billing", element: <Invoices /> },
      { path: "*", element: <NotFound /> }
    ]
  }
]);
