import React, { useState } from 'react';
import {
  Truck,
  HeartHandshake,
  CheckCircle,
  AlertTriangle,
  Building,
  Send,
  Boxes,
  Check,
  Download,
  Heart,
  ShieldCheck,
  Lock,
  FileCheck,
  UserCheck,
  Award,
  DollarSign,
  Receipt,
  Printer,
  Sparkles,
} from 'lucide-react';
import GlassCard from '../components/common/GlassCard';
import TruthBanner from '../components/common/TruthBanner';
import {
  DEMO_NGO_RESOURCES,
  DEMO_NGO_PARTNERS,
  DEMO_DISPATCH_RECOMMENDATION,
} from '../data/demoData';
import { useLanguage } from '../context/LanguageContext';

interface DonationCampaign {
  id: string;
  badge: string;
  title: string;
  description: string;
  target: number;
  raised: number;
  unitImpact: string;
  category: string;
}

const DONATION_CAMPAIGNS: DonationCampaign[] = [
  {
    id: 'camp-1',
    badge: '80G • 501(C)(3) TAX EXEMPT',
    title: 'Sacramento Basin Rapid Flood Relief Fund',
    description: 'Directly provisions dry meal rations, family water filters, and thermal emergency cots for Natomas & Pocket levee evacuation centers.',
    target: 200000,
    raised: 142500,
    unitImpact: '$50 provides a 72-hour family sustenance package for 4 evacuees',
    category: 'Essential Rations & Potable Water',
  },
  {
    id: 'camp-2',
    badge: 'EQUIPMENT MOBILIZATION',
    title: 'Mississippi Valley Inflatable Watercraft Fleet',
    description: 'Funds acquisition of motor-powered shallow water rescue rafts, personal flotation devices, and high-volume bilge evacuation pumps.',
    target: 120000,
    raised: 88200,
    unitImpact: '$100 provisions 4 commercial rescue vests and heavy-duty tow cables',
    category: 'Amphibious Fleet Operations',
  },
  {
    id: 'camp-3',
    badge: 'CRITICAL MEDICAL TRIAGE',
    title: 'Gulf Coastal First Aid & Mobile Clinics',
    description: 'Supplies portable defibrillators, oxygen cylinders, antivenom units, and field insulin cold-chain storage for flooded riverine counties.',
    target: 75000,
    raised: 54000,
    unitImpact: '$75 funds cold-chain transport for 30 pediatric vaccine doses',
    category: 'Paramedic & Emergency Triage',
  },
  {
    id: 'camp-4',
    badge: 'RESILIENT COMMUNICATIONS',
    title: 'Emergency Solar Microgrids & Satellite Terminals',
    description: 'Deploys ruggedized battery packs, foldable solar arrays, and satellite mesh communication hubs to cut-off lowland communities.',
    target: 60000,
    raised: 41800,
    unitImpact: '$150 keeps an islanded emergency coordination shelter online for 7 days',
    category: 'Power & Telecommunications',
  },
];

export const ReliefPage: React.FC = () => {
  const { t } = useLanguage();
  const [activeTab, setActiveTab] = useState<'ngo' | 'donor'>(() => {
    if (typeof window !== 'undefined' && window.location.search.includes('tab=donor')) {
      return 'donor';
    }
    return 'ngo';
  });

  // NGO Accreditation State
  const [isNgoVerified, setIsNgoVerified] = useState<boolean>(false);
  const [selectedOrg, setSelectedOrg] = useState<string>('Red Cross Disaster Response Unit');
  const [darpanId, setDarpanId] = useState<string>('DARPAN-DL-2024-8841');
  const [officerName, setOfficerName] = useState<string>('Capt. Rajesh Varma');
  const [badgeId, setBadgeId] = useState<string>('NDMA-OFFICER-771');
  const [verificationError, setVerificationError] = useState<string | null>(null);

  // NGO Operations State
  const [dispatched, setDispatched] = useState<boolean>(false);
  const [assignedQueues, setAssignedQueues] = useState<string[]>([]);
  const [downloadNotice, setDownloadNotice] = useState<string | null>(null);

  // Donator Portal State
  const [selectedAmount, setSelectedAmount] = useState<number>(50);
  const [customAmount, setCustomAmount] = useState<string>('');
  const [donorName, setDonorName] = useState<string>('Pravaha Philanthropic Patron');
  const [donorEmail, setDonorEmail] = useState<string>('patron@pravaha-relief.org');
  const [activeDonationCampaign, setActiveDonationCampaign] = useState<DonationCampaign>(DONATION_CAMPAIGNS[0]);
  const [receiptModal, setReceiptModal] = useState<{
    receiptNo: string;
    amount: number;
    campaign: string;
    donorName: string;
    timestamp: string;
  } | null>(null);

  const handleVerifyNgo = (e: React.FormEvent) => {
    e.preventDefault();
    if (!darpanId.trim() || !officerName.trim() || !badgeId.trim()) {
      setVerificationError('All accreditation fields (Registration ID, Officer Name, Badge Number) are required by statutory protocol.');
      return;
    }
    setVerificationError(null);
    setIsNgoVerified(true);
  };

  const handleQuickDemoVerify = () => {
    setSelectedOrg('International Red Cross & Disaster Unit');
    setDarpanId('DARPAN-NDMA-2024-9042');
    setOfficerName('Dr. Emily Vance (Field Director)');
    setBadgeId('FEMA-DISPATCH-882');
    setIsNgoVerified(true);
    setVerificationError(null);
  };

  const handleAuthorize = () => {
    setDispatched(true);
  };

  const handleQuickAssign = (item: string) => {
    if (!assignedQueues.includes(item)) {
      setAssignedQueues([...assignedQueues, item]);
    }
  };

  const handleDownloadCsv = () => {
    const headers = 'Resource_ID,Category,Title,Available,Allocated,In_Transit,Total,Unit\n';
    const rows = DEMO_NGO_RESOURCES.map(
      (r) =>
        `${r.id},${r.category},"${r.title}",${r.available_units},${r.allocated_units},${r.in_transit_units},${r.total_units},${r.unit_name}`
    ).join('\n');
    const blob = new Blob([headers + rows], { type: 'text/csv' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = 'pravaha_ngo_relief_inventory.csv';
    a.click();
    URL.revokeObjectURL(url);
    setDownloadNotice('Inventory CSV exported successfully.');
    setTimeout(() => setDownloadNotice(null), 3000);
  };

  const handleProcessDonation = (campaign: DonationCampaign) => {
    const finalAmount = customAmount ? parseFloat(customAmount) || selectedAmount : selectedAmount;
    const receipt = {
      receiptNo: `PRV-80G-${Math.floor(100000 + Math.random() * 900000)}`,
      amount: finalAmount,
      campaign: campaign.title,
      donorName: donorName.trim() || 'Anonymous Donor',
      timestamp: new Date().toLocaleString('en-US', { dateStyle: 'medium', timeStyle: 'short' }),
    };
    setReceiptModal(receipt);
  };

  return (
    <div className="space-y-6 pb-16">
      {/* Truth Disclaimer Banner */}
      <TruthBanner
        type="demo"
        title="RELIEF LOGISTICS & PHILANTHROPIC RELIEF HUB — SIMULATION PLATFORM"
        description="Hydrologic corridor elevation buffers and automated supply chain routing are engineering demonstration prototypes. NGO accreditation and donation transactions operate in demonstration test mode."
      />

      {/* Main Header & Dual-Portal Selection Switch */}
      <div className="flex flex-col lg:flex-row lg:items-center justify-between gap-6 p-6 sm:p-8 rounded-3xl bg-white/85 border border-[#D8E8F0] shadow-ocean backdrop-blur-xl">
        <div className="space-y-2 max-w-2xl">
          <div className="flex items-center gap-2">
            <span className="text-[10px] font-bold tracking-widest uppercase text-[#006297] bg-[#287BB5]/10 px-2.5 py-0.5 rounded-full border border-[#287BB5]/20">
              PRAVAHA RELIEF COORDINATOR
            </span>
            <span className="text-xs font-semibold text-[#6688A1]">• Dual-Portal Emergency Network</span>
          </div>
          <h1 className="text-2xl sm:text-3xl font-extrabold text-[#17354D] tracking-tight">
            {t('relief.title')}
          </h1>
          <p className="text-xs sm:text-sm text-[#36556C] leading-relaxed">
            Coordinating verified non-governmental disaster brigades, amphibious supply routes, and direct citizen philanthropic support during catastrophic inundation events.
          </p>
        </div>

        {/* Clear Two-Portal Switcher */}
        <div className="flex items-center p-1.5 rounded-2xl bg-[#EFF6FA] border border-[#D8E8F0] shadow-sm self-start lg:self-auto">
          <button
            onClick={() => setActiveTab('ngo')}
            className={`px-4 sm:px-5 py-2.5 rounded-xl text-xs font-bold transition-all flex items-center gap-2 ${
              activeTab === 'ngo'
                ? 'bg-[#006297] text-white shadow-marine'
                : 'text-[#36556C] hover:text-[#006297]'
            }`}
          >
            <ShieldCheck className="w-4 h-4" />
            <span>NGO Operations Portal</span>
            {isNgoVerified ? (
              <span className="w-2 h-2 rounded-full bg-[#10B981] animate-pulse" />
            ) : (
              <span className="w-2 h-2 rounded-full bg-[#E58C47]" />
            )}
          </button>
          <button
            onClick={() => setActiveTab('donor')}
            className={`px-4 sm:px-5 py-2.5 rounded-xl text-xs font-bold transition-all flex items-center gap-2 ${
              activeTab === 'donor'
                ? 'bg-[#006297] text-white shadow-marine'
                : 'text-[#36556C] hover:text-[#006297]'
            }`}
          >
            <HeartHandshake className="w-4 h-4 text-[#D95F62]" />
            <span>Public Donator Portal</span>
            <span className="text-[9px] font-extrabold px-1.5 py-0.2 rounded-full bg-[#10B981]/15 text-[#10B981]">
              80G
            </span>
          </button>
        </div>
      </div>

      {downloadNotice && (
        <div className="p-3.5 rounded-2xl bg-[#40A77A]/15 border border-[#40A77A]/30 text-xs font-semibold text-[#2D7857] flex items-center gap-2 animate-fadeIn">
          <CheckCircle className="w-4 h-4 text-[#40A77A]" />
          <span>{downloadNotice}</span>
        </div>
      )}

      {/* ========================================================================= */}
      {/* TAB 1: NGO OPERATIONS PORTAL (MANDATORY VERIFICATION GATE REQUIRED)     */}
      {/* ========================================================================= */}
      {activeTab === 'ngo' && (
        <div className="space-y-6">
          {!isNgoVerified ? (
            /* MANDATORY NGO VERIFICATION GATE */
            <GlassCard elevation={2} className="p-6 sm:p-10 border-2 border-[#287BB5]/30 space-y-6 bg-gradient-to-br from-white via-[#EFF6FA] to-white">
              <div className="flex flex-col md:flex-row items-start md:items-center justify-between gap-4 pb-6 border-b border-[#D8E8F0]">
                <div className="flex items-center gap-4">
                  <div className="w-14 h-14 rounded-2xl bg-[#006297]/10 text-[#006297] flex items-center justify-center shrink-0 border border-[#006297]/20">
                    <Lock className="w-7 h-7 text-[#006297]" />
                  </div>
                  <div>
                    <div className="flex items-center gap-2">
                      <span className="text-[10px] font-extrabold tracking-widest text-[#B55914] bg-[#E58C47]/15 px-2.5 py-0.5 rounded-full uppercase">
                        Statutory Protocol Gate
                      </span>
                      <span className="text-xs font-bold text-[#A92A2D]">• Verification Mandatory</span>
                    </div>
                    <h2 className="text-xl sm:text-2xl font-black text-[#17354D] mt-1">
                      NGO Humanitarian Operations Verification
                    </h2>
                    <p className="text-xs sm:text-sm text-[#36556C] mt-0.5 max-w-xl">
                      Under National Disaster Management Authority (NDMA) and FEMA emergency guidelines, access to priority supply corridor dispatch and levee stockpile requisition requires verified partner credentials.
                    </p>
                  </div>
                </div>

                <button
                  type="button"
                  onClick={handleQuickDemoVerify}
                  className="px-3.5 py-2 rounded-xl text-xs font-bold text-[#006297] bg-white border border-[#287BB5]/30 hover:bg-[#EFF6FA] transition-all flex items-center gap-1.5 shadow-sm shrink-0"
                >
                  <Sparkles className="w-3.5 h-3.5 text-[#287BB5]" />
                  <span>Quick-Verify Demo Partner</span>
                </button>
              </div>

              {verificationError && (
                <div className="p-3.5 rounded-xl bg-[#D95F62]/10 border border-[#D95F62]/30 text-xs font-semibold text-[#A92A2D] flex items-center gap-2">
                  <AlertTriangle className="w-4 h-4 text-[#D95F62] shrink-0" />
                  <span>{verificationError}</span>
                </div>
              )}

              <form onSubmit={handleVerifyNgo} className="grid grid-cols-1 md:grid-cols-2 gap-6 pt-2">
                <div className="space-y-2">
                  <label className="text-xs font-bold uppercase tracking-wider text-[#17354D] flex items-center gap-1.5">
                    <Building className="w-3.5 h-3.5 text-[#006297]" />
                    <span>Registered NGO / Relief Agency</span>
                  </label>
                  <select
                    value={selectedOrg}
                    onChange={(e) => setSelectedOrg(e.target.value)}
                    className="w-full px-4 py-3 rounded-xl bg-white border border-[#D8E8F0] text-sm font-semibold text-[#17354D] focus:outline-none focus:border-[#006297]"
                  >
                    <option value="Red Cross Disaster Response Unit">Indian Red Cross / American Red Cross Society</option>
                    <option value="Goonj Rahat Flood Response Network">Goonj Rahat Flood Response Network</option>
                    <option value="SEEDS India Disaster Resilience Brigades">SEEDS India Disaster Resilience Brigades</option>
                    <option value="Doctors Without Borders (MSF) Surge Corps">Doctors Without Borders (MSF) Surge Corps</option>
                    <option value="Pacific Delta Marine Rescue Unit">Pacific Delta Marine Rescue Unit</option>
                    <option value="Save The Children Humanitarian Logistics">Save The Children Humanitarian Logistics</option>
                  </select>
                  <p className="text-[11px] text-[#6688A1]">
                    Must be listed in the Central Disaster Registry or State NGO Directory.
                  </p>
                </div>

                <div className="space-y-2">
                  <label className="text-xs font-bold uppercase tracking-wider text-[#17354D] flex items-center gap-1.5">
                    <FileCheck className="w-3.5 h-3.5 text-[#006297]" />
                    <span>Accreditation ID (DARPAN / FEMA / UNDAC)</span>
                  </label>
                  <input
                    type="text"
                    value={darpanId}
                    onChange={(e) => setDarpanId(e.target.value)}
                    placeholder="e.g. DARPAN-MH-2024-9128 or FEMA-NGO-4401"
                    className="w-full px-4 py-3 rounded-xl bg-white border border-[#D8E8F0] text-sm font-semibold text-[#17354D] focus:outline-none focus:border-[#006297]"
                  />
                  <p className="text-[11px] text-[#6688A1]">
                    Government portal registration key used for logistics corridor clearance.
                  </p>
                </div>

                <div className="space-y-2">
                  <label className="text-xs font-bold uppercase tracking-wider text-[#17354D] flex items-center gap-1.5">
                    <UserCheck className="w-3.5 h-3.5 text-[#006297]" />
                    <span>Authorized Duty Officer Full Name</span>
                  </label>
                  <input
                    type="text"
                    value={officerName}
                    onChange={(e) => setOfficerName(e.target.value)}
                    placeholder="e.g. Capt. Rajesh Varma"
                    className="w-full px-4 py-3 rounded-xl bg-white border border-[#D8E8F0] text-sm font-semibold text-[#17354D] focus:outline-none focus:border-[#006297]"
                  />
                  <p className="text-[11px] text-[#6688A1]">
                    Field incident commander authorizing asset movement.
                  </p>
                </div>

                <div className="space-y-2">
                  <label className="text-xs font-bold uppercase tracking-wider text-[#17354D] flex items-center gap-1.5">
                    <Award className="w-3.5 h-3.5 text-[#006297]" />
                    <span>Officer Security Badge Number</span>
                  </label>
                  <input
                    type="text"
                    value={badgeId}
                    onChange={(e) => setBadgeId(e.target.value)}
                    placeholder="e.g. NDMA-OFFICER-771"
                    className="w-full px-4 py-3 rounded-xl bg-white border border-[#D8E8F0] text-sm font-semibold text-[#17354D] focus:outline-none focus:border-[#006297]"
                  />
                  <p className="text-[11px] text-[#6688A1]">
                    Issued by district emergency operations center.
                  </p>
                </div>

                <div className="md:col-span-2 pt-4 flex flex-col sm:flex-row items-center justify-between gap-4">
                  <div className="flex items-center gap-2 text-xs text-[#2D7857] font-semibold">
                    <ShieldCheck className="w-4 h-4 text-[#40A77A]" />
                    <span>Zero Data Leakage • Cryptographic Session Hash Encrypted</span>
                  </div>
                  <button
                    type="submit"
                    className="w-full sm:w-auto px-8 py-3.5 rounded-xl text-sm font-extrabold text-white bg-gradient-to-r from-[#006297] to-[#287BB5] hover:opacity-95 shadow-marine transition-all flex items-center justify-center gap-2"
                  >
                    <CheckCircle className="w-4 h-4" />
                    <span>Verify Credentials & Unlock Operations Console</span>
                  </button>
                </div>
              </form>
            </GlassCard>
          ) : (
            /* VERIFIED ACTIVE SESSION BADGE */
            <div className="p-4 sm:p-5 rounded-2xl bg-[#40A77A]/12 border-2 border-[#40A77A]/30 flex flex-col md:flex-row items-start md:items-center justify-between gap-4 shadow-sm animate-fadeIn">
              <div className="flex items-center gap-3.5">
                <div className="w-11 h-11 rounded-xl bg-[#40A77A] text-white flex items-center justify-center font-bold shadow-sm">
                  <ShieldCheck className="w-6 h-6" />
                </div>
                <div>
                  <div className="flex items-center gap-2">
                    <span className="text-[10px] font-extrabold px-2 py-0.5 rounded-full bg-[#40A77A] text-white uppercase tracking-wider">
                      Verified NGO Session Active
                    </span>
                    <span className="text-xs font-mono font-bold text-[#17354D]">
                      ID: {darpanId}
                    </span>
                  </div>
                  <div className="text-sm font-extrabold text-[#17354D] mt-0.5">
                    {selectedOrg} • Officer {officerName} ({badgeId})
                  </div>
                </div>
              </div>

              <div className="flex items-center gap-3 self-end md:self-auto">
                <span className="text-xs font-semibold text-[#2D7857] hidden sm:inline">
                  Full Dispatch Authority Granted
                </span>
                <button
                  onClick={() => setIsNgoVerified(false)}
                  className="px-3 py-1.5 rounded-lg text-xs font-bold text-[#6688A1] hover:text-[#A92A2D] bg-white border border-[#D8E8F0] hover:border-[#D95F62]/40 transition-all"
                >
                  Relinquish Credential
                </button>
              </div>
            </div>
          )}

          {/* AI Smart Coordinator Section (Hero Dispatch Allocation) */}
          <GlassCard
            elevation={1}
            className={`p-6 sm:p-8 space-y-6 bg-gradient-to-br from-white/95 via-white/85 to-[#EFF6FA] transition-all ${
              !isNgoVerified ? 'opacity-50 pointer-events-none select-none filter blur-[1px]' : ''
            }`}
          >
            <div className="flex flex-wrap items-center justify-between gap-3 pb-3 border-b border-[#D8E8F0]">
              <div className="flex items-center gap-3">
                <div className="w-10 h-10 rounded-xl bg-[#006297]/10 text-[#006297] flex items-center justify-center">
                  <Truck className="w-5 h-5" />
                </div>
                <div>
                  <div className="flex items-center gap-2">
                    <span className="text-[10px] font-bold tracking-wider text-[#006297] uppercase">
                      PRAVAHA SMART COORDINATOR
                    </span>
                    <span className="px-2 py-0.5 rounded text-[10px] font-bold bg-[#E58C47]/10 text-[#B55914] uppercase tracking-wider">
                      Simulated Allocation
                    </span>
                  </div>
                  <h2 className="text-base sm:text-lg font-extrabold text-[#17354D]">
                    Priority Dispatch Recommendation #{DEMO_DISPATCH_RECOMMENDATION.id}
                  </h2>
                </div>
              </div>

              <span className="px-3 py-1 rounded-full bg-[#D95F62]/15 text-[#A92A2D] text-xs font-bold flex items-center gap-1.5">
                <span className="w-2 h-2 rounded-full bg-[#D95F62] animate-ping" />
                <span>Critical Need Window (&lt; 2h)</span>
              </span>
            </div>

            <div className="grid grid-cols-1 xl:grid-cols-12 gap-6">
              {/* Main Recommendation Details (8 cols) */}
              <div className="xl:col-span-8 space-y-4">
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4 p-4 rounded-2xl bg-[#EFF6FA] border border-[#D8E8F0]">
                  {/* Needs & Match */}
                  <div className="space-y-3">
                    <div>
                      <span className="text-[10px] font-bold uppercase tracking-wider text-[#6688A1]">
                        Target Objective
                      </span>
                      <div className="text-sm font-bold text-[#17354D]">
                        350 Food Packets & First Aid Kits
                      </div>
                      <div className="text-xs text-[#006297] flex items-center gap-1 mt-0.5">
                        <Building className="w-3.5 h-3.5" />
                        <span>Sacramento Community Shelter #2 (Natomas)</span>
                      </div>
                    </div>

                    <div className="pt-2 border-t border-[#D8E8F0]">
                      <span className="text-[10px] font-bold uppercase tracking-wider text-[#6688A1]">
                        Optimized Match Supplier
                      </span>
                      <div className="flex justify-between items-baseline">
                        <span className="text-xs font-bold text-[#17354D]">Pacific Disaster Response</span>
                        <span className="text-[11px] font-mono font-bold text-[#40A77A]">3.2 km Away</span>
                      </div>
                      <p className="text-[11px] text-[#6688A1] mt-0.5">
                        Central Warehouse #3 inventory confirms 500 dry meal rations ready for immediate payload.
                      </p>
                    </div>
                  </div>

                  {/* Route Feasibility */}
                  <div className="p-3.5 rounded-xl bg-white border border-[#D8E8F0] space-y-3 flex flex-col justify-between">
                    <div className="p-2.5 rounded-lg bg-[#D95F62]/10 text-[#A92A2D] text-xs space-y-0.5">
                      <div className="font-bold flex items-center gap-1.5">
                        <AlertTriangle className="w-3.5 h-3.5" />
                        <span>Hydro-Gauge Inflow Warning</span>
                      </div>
                      <p className="text-[11px]">
                        River Reach 04 projected +1.2m elevation surge within next 6 hours.
                      </p>
                    </div>

                    <div className="space-y-1">
                      <div className="flex justify-between items-center text-xs">
                        <span className="font-semibold text-[#17354D]">Corridor Feasibility</span>
                        <span className="font-mono font-bold text-[#2D7857]">98% High-Grade Clear</span>
                      </div>
                      <div className="w-full bg-[#D8E8F0] h-2 rounded-full overflow-hidden">
                        <div className="bg-[#40A77A] h-full rounded-full" style={{ width: '98%' }} />
                      </div>
                      <div className="flex items-center gap-1 text-[11px] text-[#2D7857] font-semibold">
                        <CheckCircle className="w-3 h-3 shrink-0" />
                        <span>Safe via Hwy 160 Corridor (+1.8m safe vertical freeboard above surge line) • Simulated Elevation Check</span>
                      </div>
                    </div>

                    <button
                      onClick={handleAuthorize}
                      disabled={dispatched}
                      className={`w-full py-2.5 rounded-xl text-xs font-bold transition-all flex items-center justify-center gap-1.5 shadow-sm ${
                        dispatched
                          ? 'bg-[#40A77A] text-white'
                          : 'bg-[#006297] text-white hover:bg-[#287BB5]'
                      }`}
                    >
                      {dispatched ? (
                        <>
                          <Check className="w-4 h-4" />
                          <span>Authorized & Dispatched to Field Crew</span>
                        </>
                      ) : (
                        <>
                          <Send className="w-4 h-4" />
                          <span>Authorize & Dispatch Recommendation</span>
                        </>
                      )}
                    </button>
                  </div>
                </div>
              </div>

              {/* Pending Matches Live Queue (4 cols) */}
              <div className="xl:col-span-4 p-4 rounded-2xl bg-[#EFF6FA] border border-[#D8E8F0] space-y-3">
                <div className="flex items-center justify-between">
                  <span className="text-xs font-bold text-[#17354D]">Pending AI Matches</span>
                  <span className="text-[10px] font-mono font-bold bg-white px-2 py-0.5 rounded-full border border-[#D8E8F0]">
                    3 In Queue
                  </span>
                </div>

                <div className="space-y-2.5">
                  <div className="p-3 rounded-xl bg-white border border-[#D8E8F0] space-y-1">
                    <div className="flex justify-between items-center">
                      <span className="font-bold text-xs text-[#17354D]">60 Life Vests</span>
                      <span className="px-1.5 py-0.5 rounded text-[10px] font-bold bg-[#D95F62]/10 text-[#D95F62]">
                        Priority 1
                      </span>
                    </div>
                    <div className="text-[11px] text-[#6688A1]">
                      Dest: Sector 4 Riverfront Depot • Match: Delta Rescue
                    </div>
                    <div className="flex justify-between items-center pt-1">
                      <span className="text-[10px] text-[#2D7857] font-semibold">ETA 24 mins • Clearance OK</span>
                      <button
                        onClick={() => handleQuickAssign('Life Vests')}
                        disabled={assignedQueues.includes('Life Vests')}
                        className="px-2 py-0.5 rounded-lg text-[10px] font-bold bg-[#EFF6FA] text-[#006297] hover:bg-[#D8E8F0]"
                      >
                        {assignedQueues.includes('Life Vests') ? 'Assigned' : 'Quick Assign'}
                      </button>
                    </div>
                  </div>

                  <div className="p-3 rounded-xl bg-white border border-[#D8E8F0] space-y-1">
                    <div className="flex justify-between items-center">
                      <span className="font-bold text-xs text-[#17354D]">2,000L Potable Water</span>
                      <span className="px-1.5 py-0.5 rounded text-[10px] font-bold bg-[#E58C47]/10 text-[#E58C47]">
                        Priority 2
                      </span>
                    </div>
                    <div className="text-[11px] text-[#6688A1]">
                      Dest: Yuba City Civic Refuge • Match: AquaSafe
                    </div>
                    <div className="flex justify-between items-center pt-1">
                      <span className="text-[10px] text-[#2D7857] font-semibold">ETA 45 mins • Causeway Verified</span>
                      <button
                        onClick={() => handleQuickAssign('Potable Water')}
                        disabled={assignedQueues.includes('Potable Water')}
                        className="px-2 py-0.5 rounded-lg text-[10px] font-bold bg-[#EFF6FA] text-[#006297] hover:bg-[#D8E8F0]"
                      >
                        {assignedQueues.includes('Potable Water') ? 'Assigned' : 'Quick Assign'}
                      </button>
                    </div>
                  </div>

                  <div className="p-3 rounded-xl bg-white border border-[#D8E8F0] space-y-1">
                    <div className="flex justify-between items-center">
                      <span className="font-bold text-xs text-[#17354D]">12 Certified Paramedics</span>
                      <span className="px-1.5 py-0.5 rounded text-[10px] font-bold bg-[#D95F62]/10 text-[#D95F62]">
                        Critical Medical
                      </span>
                    </div>
                    <div className="text-[11px] text-[#6688A1]">
                      Dest: Natomas Evac Center • Match: Red Cross Unit 7
                    </div>
                    <div className="flex justify-between items-center pt-1">
                      <span className="text-[10px] text-[#2D7857] font-semibold">ETA 18 mins • High Ground</span>
                      <button
                        onClick={() => handleQuickAssign('Paramedics')}
                        disabled={assignedQueues.includes('Paramedics')}
                        className="px-2 py-0.5 rounded-lg text-[10px] font-bold bg-[#EFF6FA] text-[#006297] hover:bg-[#D8E8F0]"
                      >
                        {assignedQueues.includes('Paramedics') ? 'Assigned' : 'Quick Assign'}
                      </button>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </GlassCard>

          {/* Live Basin Resource Inventory Matrix (4 Glass Metric Cards) */}
          <div className={`space-y-4 ${!isNgoVerified ? 'opacity-50 pointer-events-none' : ''}`}>
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-2">
                <Boxes className="w-5 h-5 text-[#006297]" />
                <h2 className="text-base sm:text-lg font-bold text-[#17354D]">
                  Live Basin Resource Inventory Matrix
                </h2>
                <span className="px-2 py-0.5 rounded text-[10px] font-bold bg-[#E58C47]/10 text-[#B55914] uppercase tracking-wider">
                  Simulated Stockpile Feed
                </span>
              </div>
              <div className="flex items-center gap-3">
                <span className="text-xs font-mono text-[#6688A1]">Telemetry Synced: 42s ago</span>
                <button
                  onClick={handleDownloadCsv}
                  className="flex items-center gap-1 text-xs font-bold text-[#006297] hover:underline"
                >
                  <Download className="w-3.5 h-3.5" />
                  <span>Export CSV</span>
                </button>
              </div>
            </div>

            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
              {DEMO_NGO_RESOURCES.map((res) => (
                <GlassCard key={res.id} elevation={1} className="p-5 flex flex-col justify-between">
                  <div className="space-y-2">
                    <div className="flex items-center justify-between">
                      <span className="text-[10px] font-bold uppercase tracking-wider text-[#6688A1]">
                        {res.category}
                      </span>
                      <span className="text-xs font-bold font-mono text-[#40A77A]">
                        {Math.round((res.available_units / res.total_units) * 100)}% Ready
                      </span>
                    </div>

                    <div>
                      <h3 className="font-bold text-sm text-[#17354D]">{res.title}</h3>
                      <div className="text-2xl font-extrabold text-[#17354D] font-mono mt-1">
                        {res.available_units.toLocaleString()}
                        <span className="text-xs font-normal text-[#6688A1] ml-1.5">{res.unit_name}</span>
                      </div>
                    </div>

                    <div className="space-y-1 pt-2 border-t border-[#D8E8F0] text-xs">
                      <div className="flex justify-between text-[#6688A1]">
                        <span>Allocated / Active:</span>
                        <span className="font-mono font-semibold text-[#17354D]">
                          {res.allocated_units} {res.unit_name}
                        </span>
                      </div>
                      <div className="flex justify-between text-[#6688A1]">
                        <span>In-Transit:</span>
                        <span className="font-mono font-semibold text-[#006297]">
                          {res.in_transit_units} {res.unit_name}
                        </span>
                      </div>
                    </div>
                  </div>
                </GlassCard>
              ))}
            </div>
          </div>

          {/* Verified Partner Directory */}
          <GlassCard elevation={1} className="p-6 sm:p-8 space-y-4">
            <div className="flex items-center justify-between pb-3 border-b border-[#D8E8F0]">
              <div>
                <h3 className="text-base font-bold text-[#17354D]">
                  Verified NGO Relief Partner Directory
                </h3>
                <p className="text-xs text-[#6688A1]">
                  First-response rescue brigades registered with state disaster authorities.
                </p>
              </div>
              <span className="text-xs font-mono font-bold text-[#006297]">
                {DEMO_NGO_PARTNERS.length} Brigades Armed
              </span>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
              {DEMO_NGO_PARTNERS.map((partner) => (
                <div
                  key={partner.id}
                  className="p-4 rounded-xl bg-[#EFF6FA] border border-[#D8E8F0] space-y-2 flex flex-col justify-between"
                >
                  <div className="space-y-1">
                    <div className="flex items-center justify-between">
                      <span
                        className={`px-2 py-0.5 rounded-full text-[10px] font-bold ${
                          partner.readiness === 'ACTIVE_DEPLOY'
                            ? 'bg-[#40A77A]/15 text-[#2D7857]'
                            : 'bg-[#287BB5]/15 text-[#006297]'
                        }`}
                      >
                        {partner.readiness}
                      </span>
                      <span className="text-xs font-mono font-bold text-[#17354D]">
                        {partner.active_teams} Teams
                      </span>
                    </div>
                    <h4 className="font-bold text-sm text-[#17354D]">{partner.name}</h4>
                    <p className="text-[11px] text-[#6688A1]">{partner.operating_zone}</p>
                  </div>

                  <div className="pt-2 border-t border-[#D8E8F0] flex justify-between items-center text-xs">
                    <span className="font-mono text-[11px] text-[#36556C]">{partner.contact}</span>
                    <span className="text-[10px] font-bold text-[#006297]">Verified NGO</span>
                  </div>
                </div>
              ))}
            </div>
          </GlassCard>
        </div>
      )}

      {/* ========================================================================= */}
      {/* TAB 2: PUBLIC DONATOR PORTAL (DEDICATED EXPERIENCE FOR DONORS)           */}
      {/* ========================================================================= */}
      {activeTab === 'donor' && (
        <div className="space-y-6 animate-fadeIn">
          {/* Tax Exemption Receipt Modal */}
          {receiptModal && (
            <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/50 backdrop-blur-sm animate-fadeIn">
              <div className="w-full max-w-lg bg-white rounded-3xl p-6 sm:p-8 shadow-2xl border border-[#D8E8F0] space-y-5">
                <div className="flex items-center justify-between pb-4 border-b border-[#D8E8F0]">
                  <div className="flex items-center gap-3">
                    <div className="w-10 h-10 rounded-xl bg-[#40A77A]/15 text-[#2D7857] flex items-center justify-center">
                      <Receipt className="w-5 h-5 text-[#40A77A]" />
                    </div>
                    <div>
                      <span className="text-[10px] font-extrabold uppercase text-[#2D7857] tracking-wider">
                        Official Tax Exemption Receipt
                      </span>
                      <h3 className="text-base font-extrabold text-[#17354D]">
                        Section 80G / 501(c)(3) Certificate
                      </h3>
                    </div>
                  </div>
                  <button
                    onClick={() => setReceiptModal(null)}
                    className="w-8 h-8 rounded-full bg-[#EFF6FA] hover:bg-[#D8E8F0] flex items-center justify-center text-sm font-bold text-[#6688A1]"
                  >
                    ✕
                  </button>
                </div>

                <div className="space-y-3 p-4 rounded-2xl bg-[#EFF6FA] border border-[#D8E8F0] text-xs">
                  <div className="flex justify-between py-1 border-b border-[#D8E8F0]/60">
                    <span className="text-[#6688A1]">Receipt Voucher ID:</span>
                    <span className="font-mono font-bold text-[#17354D]">{receiptModal.receiptNo}</span>
                  </div>
                  <div className="flex justify-between py-1 border-b border-[#D8E8F0]/60">
                    <span className="text-[#6688A1]">Philanthropic Benefactor:</span>
                    <span className="font-semibold text-[#17354D]">{receiptModal.donorName}</span>
                  </div>
                  <div className="flex justify-between py-1 border-b border-[#D8E8F0]/60">
                    <span className="text-[#6688A1]">Allocated Campaign:</span>
                    <span className="font-semibold text-[#006297] text-right">{receiptModal.campaign}</span>
                  </div>
                  <div className="flex justify-between py-1 border-b border-[#D8E8F0]/60">
                    <span className="text-[#6688A1]">Contribution Amount:</span>
                    <span className="text-base font-mono font-extrabold text-[#2D7857]">
                      ${receiptModal.amount.toLocaleString()} USD
                    </span>
                  </div>
                  <div className="flex justify-between py-1">
                    <span className="text-[#6688A1]">Timestamp of Transaction:</span>
                    <span className="font-mono text-[#17354D]">{receiptModal.timestamp}</span>
                  </div>
                </div>

                <div className="p-3 rounded-xl bg-[#40A77A]/10 border border-[#40A77A]/20 text-[11px] text-[#2D7857] leading-relaxed">
                  ✓ This digital voucher certifies tax-exempt deduction under 80G (Indian Income Tax Act) and 501(c)(3) IRS code for emergency disaster relief provisions.
                </div>

                <div className="flex items-center justify-end gap-3 pt-2">
                  <button
                    onClick={() => {
                      window.print();
                    }}
                    className="px-4 py-2.5 rounded-xl text-xs font-bold text-[#006297] bg-[#EFF6FA] hover:bg-[#D8E8F0] transition-all flex items-center gap-1.5"
                  >
                    <Printer className="w-3.5 h-3.5" />
                    <span>Print Receipt</span>
                  </button>
                  <button
                    onClick={() => setReceiptModal(null)}
                    className="px-5 py-2.5 rounded-xl text-xs font-bold text-white bg-[#006297] hover:bg-[#287BB5] transition-all"
                  >
                    Done & Close
                  </button>
                </div>
              </div>
            </div>
          )}

          {/* Donator Hero Banner */}
          <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
            <GlassCard elevation={2} className="lg:col-span-8 p-6 sm:p-8 space-y-4 bg-gradient-to-br from-white via-white/95 to-[#EFF6FA]">
              <div className="flex items-center gap-2">
                <span className="px-2.5 py-0.5 rounded-full bg-[#D95F62]/10 text-[#A92A2D] text-[10px] font-extrabold uppercase tracking-wider">
                  Citizen & Corporate Philanthropy
                </span>
                <span className="text-xs font-bold text-[#2D7857]">• 100% Direct Field Allocation</span>
              </div>
              <h2 className="text-xl sm:text-2xl font-black text-[#17354D]">
                Fund Life-Saving Riverine Relief & Emergency Fleets
              </h2>
              <p className="text-xs sm:text-sm text-[#36556C] leading-relaxed">
                Every contribution is immediately converted into dry meal rations, potable purification kits, and amphibious flood rescue watercraft deployed directly along verified safe elevation corridors.
              </p>

              {/* Fund Transparency Audit Grid */}
              <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 pt-2">
                <div className="p-3 rounded-xl bg-white border border-[#D8E8F0] space-y-0.5">
                  <span className="text-[10px] font-bold text-[#6688A1] uppercase">Direct Field Supplies</span>
                  <div className="text-base font-black text-[#17354D] font-mono">88.0%</div>
                  <span className="text-[10px] text-[#2D7857]">Food, water, rafts</span>
                </div>
                <div className="p-3 rounded-xl bg-white border border-[#D8E8F0] space-y-0.5">
                  <span className="text-[10px] font-bold text-[#6688A1] uppercase">Cold-Chain Logistics</span>
                  <div className="text-base font-black text-[#17354D] font-mono">8.0%</div>
                  <span className="text-[10px] text-[#006297]">Fuel & vehicles</span>
                </div>
                <div className="p-3 rounded-xl bg-white border border-[#D8E8F0] space-y-0.5">
                  <span className="text-[10px] font-bold text-[#6688A1] uppercase">Telemetry Sentinel</span>
                  <div className="text-base font-black text-[#17354D] font-mono">4.0%</div>
                  <span className="text-[10px] text-[#006297]">Route QA checks</span>
                </div>
                <div className="p-3 rounded-xl bg-white border border-[#D8E8F0] space-y-0.5">
                  <span className="text-[10px] font-bold text-[#6688A1] uppercase">Admin Overhead</span>
                  <div className="text-base font-black text-[#40A77A] font-mono">0.0%</div>
                  <span className="text-[10px] text-[#2D7857]">Corporate subsidized</span>
                </div>
              </div>
            </GlassCard>

            {/* Instant Contribution Panel */}
            <GlassCard elevation={2} className="lg:col-span-4 p-6 space-y-4 bg-white border-2 border-[#287BB5]/20 flex flex-col justify-between">
              <div className="space-y-3">
                <div className="flex items-center justify-between pb-2 border-b border-[#D8E8F0]">
                  <span className="text-xs font-extrabold text-[#17354D] uppercase tracking-wider">
                    Quick Contribution
                  </span>
                  <span className="text-[10px] font-mono font-bold text-[#006297] bg-[#EFF6FA] px-2 py-0.5 rounded-full">
                    Instant 80G Receipt
                  </span>
                </div>

                <div className="space-y-1.5">
                  <label className="text-[11px] font-bold text-[#6688A1] uppercase">Select Contribution Amount</label>
                  <div className="grid grid-cols-4 gap-2">
                    {[25, 50, 100, 250].map((amt) => (
                      <button
                        key={amt}
                        type="button"
                        onClick={() => {
                          setSelectedAmount(amt);
                          setCustomAmount('');
                        }}
                        className={`py-2 rounded-xl text-xs font-extrabold transition-all ${
                          selectedAmount === amt && !customAmount
                            ? 'bg-[#006297] text-white shadow-marine'
                            : 'bg-[#EFF6FA] text-[#17354D] hover:bg-[#D8E8F0]'
                        }`}
                      >
                        ${amt}
                      </button>
                    ))}
                  </div>
                </div>

                <div className="space-y-1">
                  <label className="text-[11px] font-bold text-[#6688A1] uppercase">Or Custom USD ($)</label>
                  <div className="relative">
                    <DollarSign className="w-4 h-4 text-[#6688A1] absolute left-3 top-2.5" />
                    <input
                      type="number"
                      placeholder="e.g. 500"
                      value={customAmount}
                      onChange={(e) => setCustomAmount(e.target.value)}
                      className="w-full pl-9 pr-3 py-2 rounded-xl bg-[#EFF6FA] border border-[#D8E8F0] text-xs font-mono font-bold text-[#17354D] focus:outline-none focus:border-[#006297]"
                    />
                  </div>
                </div>

                <div className="space-y-1">
                  <label className="text-[11px] font-bold text-[#6688A1] uppercase">Benefactor Name (For Receipt)</label>
                  <input
                    type="text"
                    value={donorName}
                    onChange={(e) => setDonorName(e.target.value)}
                    className="w-full px-3 py-2 rounded-xl bg-[#EFF6FA] border border-[#D8E8F0] text-xs font-semibold text-[#17354D] focus:outline-none focus:border-[#006297]"
                  />
                </div>

                <div className="space-y-1">
                  <label className="text-[11px] font-bold text-[#6688A1] uppercase">Email Address (E-Receipt Delivery)</label>
                  <input
                    type="email"
                    value={donorEmail}
                    onChange={(e) => setDonorEmail(e.target.value)}
                    className="w-full px-3 py-2 rounded-xl bg-[#EFF6FA] border border-[#D8E8F0] text-xs font-semibold text-[#17354D] focus:outline-none focus:border-[#006297]"
                  />
                </div>
              </div>

              <button
                type="button"
                onClick={() => handleProcessDonation(activeDonationCampaign)}
                className="w-full py-3 rounded-xl text-xs font-extrabold text-white bg-gradient-to-r from-[#D95F62] to-[#E98985] hover:opacity-95 shadow-ambient transition-all flex items-center justify-center gap-2 mt-2"
              >
                <Heart className="w-4 h-4 fill-current" />
                <span>
                  Donate ${customAmount ? parseFloat(customAmount) || selectedAmount : selectedAmount} & Generate Receipt
                </span>
              </button>
            </GlassCard>
          </div>

          {/* 4 Dedicated Campaigns */}
          <div className="space-y-4">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-2">
                <HeartHandshake className="w-5 h-5 text-[#006297]" />
                <h3 className="text-base sm:text-lg font-bold text-[#17354D]">
                  Active Emergency Disaster Relief Campaigns
                </h3>
              </div>
              <span className="text-xs font-mono text-[#6688A1]">
                4 Campaigns Live in High-Risk Basins
              </span>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              {DONATION_CAMPAIGNS.map((camp) => {
                const pct = Math.round((camp.raised / camp.target) * 100);
                const isSelected = activeDonationCampaign.id === camp.id;
                return (
                  <GlassCard
                    key={camp.id}
                    elevation={1}
                    className={`p-6 space-y-4 flex flex-col justify-between transition-all border-2 ${
                      isSelected ? 'border-[#006297] bg-white shadow-ocean' : 'border-[#D8E8F0] bg-white/90'
                    }`}
                  >
                    <div className="space-y-2.5">
                      <div className="flex items-center justify-between">
                        <span className="px-2.5 py-0.5 rounded-full bg-[#40A77A]/15 text-[#2D7857] text-[10px] font-bold">
                          {camp.badge}
                        </span>
                        <span className="text-xs font-mono font-bold text-[#006297]">{camp.category}</span>
                      </div>

                      <h4 className="font-extrabold text-base text-[#17354D]">{camp.title}</h4>
                      <p className="text-xs text-[#6688A1] leading-relaxed">{camp.description}</p>

                      <div className="p-2.5 rounded-xl bg-[#EFF6FA] border border-[#D8E8F0] text-[11px] text-[#006297] font-semibold flex items-center gap-1.5">
                        <Sparkles className="w-3.5 h-3.5 text-[#287BB5] shrink-0" />
                        <span>{camp.unitImpact}</span>
                      </div>

                      <div className="pt-2 space-y-1">
                        <div className="flex justify-between text-xs font-bold">
                          <span className="text-[#17354D]">Raised: ${camp.raised.toLocaleString()}</span>
                          <span className="text-[#006297]">
                            Goal: ${camp.target.toLocaleString()} ({pct}%)
                          </span>
                        </div>
                        <div className="w-full h-2 rounded-full bg-[#D8E8F0] overflow-hidden">
                          <div
                            className="h-full bg-gradient-to-r from-[#006297] to-[#287BB5] rounded-full"
                            style={{ width: `${pct}%` }}
                          />
                        </div>
                      </div>
                    </div>

                    <div className="pt-4 border-t border-[#D8E8F0] flex items-center gap-3">
                      <button
                        type="button"
                        onClick={() => {
                          setActiveDonationCampaign(camp);
                          handleProcessDonation(camp);
                        }}
                        className="flex-1 py-2.5 rounded-xl text-xs font-bold text-white bg-[#006297] hover:bg-[#287BB5] transition-all flex items-center justify-center gap-1.5 shadow-sm"
                      >
                        <Heart className="w-3.5 h-3.5 fill-current" />
                        <span>Support This Campaign</span>
                      </button>
                      <button
                        type="button"
                        onClick={() => setActiveDonationCampaign(camp)}
                        className={`px-3 py-2.5 rounded-xl text-xs font-bold transition-all border ${
                          isSelected
                            ? 'bg-[#EFF6FA] border-[#006297] text-[#006297]'
                            : 'bg-white border-[#D8E8F0] text-[#6688A1] hover:text-[#17354D]'
                        }`}
                      >
                        {isSelected ? 'Selected' : 'Select'}
                      </button>
                    </div>
                  </GlassCard>
                );
              })}
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default ReliefPage;
