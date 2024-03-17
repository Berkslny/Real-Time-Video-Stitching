
library IEEE;
use IEEE.STD_LOGIC_1164.ALL;
use IEEE.NUMERIC_STD.ALL;

entity ov7670_capture is
    Port ( pclk  : in   STD_LOGIC;
           rez_160x120 : IN std_logic;
           rez_320x240 : IN std_logic;
           vsync : in   STD_LOGIC;
           href  : in   STD_LOGIC;
           d     : in   STD_LOGIC_VECTOR (7 downto 0);
           addr  : out  STD_LOGIC_VECTOR (18 downto 0);
           dout  : out  STD_LOGIC_VECTOR (11 downto 0);
           we    : out  STD_LOGIC);
end ov7670_capture;

architecture Behavioral of ov7670_capture is
   signal d_latch      : std_logic_vector(15 downto 0) := (others => '0');
   signal address      : STD_LOGIC_VECTOR(18 downto 0) := (others => '0');
   signal line         : std_logic_vector(1 downto 0)  := (others => '0');
   signal href_last    : std_logic_vector(6 downto 0)  := (others => '0');
   signal we_reg       : std_logic := '0';
   signal href_hold    : std_logic := '0';
   signal latched_vsync : STD_LOGIC := '0';
   signal latched_href  : STD_LOGIC := '0';
   signal latched_d     : STD_LOGIC_VECTOR (7 downto 0) := (others => '0');
begin
   addr <= address;
   we <= we_reg;
   dout    <= d_latch(15 downto 12) & d_latch(10 downto 7) & d_latch(4 downto 1); 
   
capture_process: process(pclk)
   begin
      if rising_edge(pclk) then
         if we_reg = '1' then
            address <= std_logic_vector(unsigned(address)+1);
         end if;

         -- href bir piksel transferini ba?lat?r ve bu 3 döngü sürer
         --        Input   | Saat sonras? durum  
         --         href   | wr_hold    d_latch           dout                we address  address_next
         -- döngü -1  x    |    xx      xxxxxxxxxxxxxxxx  xxxxxxxxxxxx  x   xxxx     xxxx
         -- döngü 0   1    |    x1      xxxxxxxxRRRRRGGG  xxxxxxxxxxxx  x   xxxx     addr
         -- döngü 1   0    |    10      RRRRRGGGGGGBBBBB  xxxxxxxxxxxx  x   addr     addr
         -- döngü 2   x    |    0x      GGGBBBBBxxxxxxxx  RRRRGGGGBBBB  1   addr     addr+1

         -- href üzerindeki yükselen kenar? alg?lama - tarama sat?r?n?n ba?lang?c?
         if href_hold = '0' and latched_href = '1' then
            case line is
               when "00"   => line <= "01";
               when "01"   => line <= "10";
               when "10"   => line <= "11";
               when others => line <= "00";
            end case;
         end if;
         href_hold <= latched_href;
         
         -- Kameradan veri yakalama, 12-bit RGB
         if latched_href = '1' then
            d_latch <= d_latch( 7 downto 0) & latched_d;
         end if;
         we_reg  <= '0';

         -- Yeni bir ekran ba?latmak gerekti?i zaman için (yani, yakalamay? yeniden ba?latmam?z gerekiyor)
         if latched_vsync = '1' then 
            address      <= (others => '0');
            href_last    <= (others => '0');
            line         <= (others => '0');
         else
            -- Gerek olmad???nda bir piksel yakalamam?z gerekti?inde yazma etkinle?tirmeyi ayarlar
            if (rez_160x120 = '1' and href_last(6) = '1') or
               (rez_320x240 = '1' and href_last(2) = '1') or 
               (rez_160x120 = '0' and rez_320x240  = '0' and href_last(0) = '1') then
               
               if rez_160x120 = '1' then
                  if line = "10" then
                     we_reg <= '1';
                   end if;
               elsif rez_320x240 = '1' then
                  if line(1) = '1' then
                     we_reg <= '1';
                   end if;
               else
                   we_reg <= '1';
               end if;
               href_last <= (others => '0');
            else
               href_last <= href_last(href_last'high-1 downto 0) & latched_href;
            end if;
         end if;
      end if;
      if falling_edge(pclk) then
         latched_d     <= d;
         latched_href  <= href;
         latched_vsync <= vsync;
      end if;
   end process;
end Behavioral;
