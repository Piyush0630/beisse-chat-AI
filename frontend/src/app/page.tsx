import Header from "@/components/Layout/Header";
import MainContent from "@/components/Layout/MainContent";

export default function Home() {
  return (
    <main className="flex flex-col h-screen overflow-hidden">
      <Header />
      <MainContent />
    </main>
  );
}
