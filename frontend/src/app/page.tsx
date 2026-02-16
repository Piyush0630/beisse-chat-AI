import Header from "@/components/Layout/Header";
import MainContent from "@/components/Layout/MainContent";
import TopToolbar from "@/components/TopToolbar";

export default function Home() {
  return (
    <main className="flex flex-col h-screen overflow-hidden">
      <Header />
      <TopToolbar />
      <MainContent />
    </main>
  );
}
