export interface Doctor {
  id: number;
  name: string;
  specialization: string;
  city?: string;
  rating?: number;
  distance?: number;
  address_details?: {
    address: string;
    city: string;
    state: string;
  };
  gender_name?: string;
  status?: string;
  open_time_1?: string;
  close_time_1?: string;
  open_time_2?: string;
  close_time_2?: string;
}

export interface HumanDoctor extends Doctor {
  doctor_id: number;
  phone_number?: string;
  years_experience?: number;
  first_name: string;
  last_name: string;
  yoe?: number;
  registration_number?: string;
}

export interface VetDoctor extends Doctor {
  doctor_id: number;
  contact_number?: string;
  experience?: number;
  specialty: string;
  clinic_name?: string;
  license_number?: string;
  gender?: string;
  address?: string;
}