import { render, screen } from '@testing-library/react';
import { describe, it, expect } from 'vitest';
import FailCard from '@/components/custom/FailCard';
import PassCard from '@/components/custom/PassCard';
import MinimalCard from '@/components/custom/MinimalCard';

describe('ResultCards - Unit Test (FailCard, PassCard, MinimalCard)', () => {
  // TC-FE-CARD-01: Tampilan Pesan Gagal: Cakupan Kurang
  it('TC-FE-CARD-01: displays minimal coverage message when statusEksekusi is true but coverage is below threshold', () => {
    render(
      <FailCard
        percentageCoverage={60}
        minimumCoverage={80}
        statusEksekusi={true}
        tanggalEksekusi="2026-08-17"
      />
    );

    expect(screen.getByText('Hasil Pengujian')).toBeInTheDocument();
    expect(screen.getByText('Hasil Coverage Test Case Anda 60%')).toBeInTheDocument();
    expect(
      screen.getByText(
        'Mohon maaf, belum bisa melanjutkan ke case berikutnya. Minimal coverage test 80%.'
      )
    ).toBeInTheDocument();
    expect(screen.getByText('Tanggal Eksekusi: 2026-08-17')).toBeInTheDocument();
  });

  // TC-FE-CARD-02: Tampilan Pesan Gagal: Ada Test Case Gagal
  it('TC-FE-CARD-02: displays failed test case message when statusEksekusi is false', () => {
    render(
      <FailCard
        percentageCoverage={0}
        minimumCoverage={80}
        statusEksekusi={false}
        tanggalEksekusi="2026-08-17"
      />
    );

    expect(
      screen.getByText(
        'Hasil Coverage Test Case Anda tidak dapat dihitung, karena terdapat test case yang berstatus FAILED.'
      )
    ).toBeInTheDocument();
    expect(
      screen.getByText(
        'Mohon maaf, belum bisa melanjutkan ke case berikutnya. Ubah kembali test case sampai semua hasil test result berstatus PASS.'
      )
    ).toBeInTheDocument();
  });

  // TC-FE-CARD-03: Penyajian Informasi Poin dan Tanggal pada PassCard
  it('TC-FE-CARD-03: displays points, coverage score, and execution date on PassCard', () => {
    render(
      <PassCard
        percentageCoverage={95}
        minimumCoverage={80}
        tanggalEksekusi="2026-08-17"
        poin={150}
      />
    );

    expect(screen.getByText('Hasil Pengujian')).toBeInTheDocument();
    expect(screen.getByText('Hasil Coverage Test Case Anda 95%')).toBeInTheDocument();
    expect(
      screen.getByText(
        'Selamat! Anda sudah berhasil melewati batas minimal coverage test, yaitu 80%'
      )
    ).toBeInTheDocument();
    expect(screen.getByText('150 Poin')).toBeInTheDocument();
    expect(screen.getByText('Tanggal Eksekusi: 2026-08-17')).toBeInTheDocument();
  });

  // TC-FE-CARD-04: Nilai Batas Cakupan Default pada MinimalCard
  it('TC-FE-CARD-04: renders default 80% threshold when minimumCoverage prop is omitted', () => {
    render(<MinimalCard />);

    expect(screen.getByText('Hasil Pengujian')).toBeInTheDocument();
    expect(screen.getByText('80%')).toBeInTheDocument();
  });

  // TC-FE-CARD-05: Nilai Batas Cakupan Kustom pada MinimalCard
  it('TC-FE-CARD-05: renders custom threshold when minimumCoverage prop is provided', () => {
    render(<MinimalCard minimumCoverage={90} />);

    expect(screen.getByText('90%')).toBeInTheDocument();
  });
});
