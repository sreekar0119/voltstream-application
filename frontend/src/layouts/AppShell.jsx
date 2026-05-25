import { AnimatePresence, motion } from "framer-motion";
import { Outlet, useLocation } from "react-router-dom";
import { DeviceAgentAssistant } from "../components/ai/DeviceAgentAssistant.jsx";
import { FloatingAssistant } from "../components/ai/FloatingAssistant.jsx";
import { Sidebar } from "../components/Sidebar.jsx";
import { Topbar } from "../components/Topbar.jsx";

export function AppShell() {
  const location = useLocation();

  return (
    <div className="relative min-h-screen overflow-hidden text-slate-100">
      <div className="aurora-grid no-print fixed inset-x-0 top-0 h-[36rem]" />
      <div className="noise no-print" />
      <div className="relative z-10 flex min-h-screen">
        <div className="no-print">
          <Sidebar />
        </div>
        <main className="min-w-0 flex-1 px-4 pb-8 pt-4 sm:px-6 lg:pl-[18rem] lg:pr-8">
          <div className="no-print">
            <Topbar />
          </div>
          <AnimatePresence mode="wait">
            <motion.div key={location.pathname} className="pt-5">
              <Outlet />
            </motion.div>
          </AnimatePresence>
        </main>
      </div>
      <div className="no-print">
        <FloatingAssistant />
        <DeviceAgentAssistant />
      </div>
    </div>
  );
}
