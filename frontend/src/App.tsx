import { BrowserRouter, Routes, Route } from "react-router-dom";

import Dashboard from "./pages/Dashboard";
import RepositoryExplorer from "./pages/RepositoryExplorer";
import FileViewer from "./pages/FileViewer";
import Chat from "./pages/Chat";
import CodeReview from "./pages/CodeReview";

function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<Dashboard />} />

        <Route
          path="/repositories/:id"
          element={<RepositoryExplorer />}
        />

        <Route
          path="/repositories/:id/chat"
          element={<Chat />}
        />

        <Route
          path="/files/:id"
          element={<FileViewer />}
        />

        <Route
          path="/files/:id/review"
          element={<CodeReview />}
        />
      </Routes>
    </BrowserRouter>
  );
}

export default App;