<template>
  <div
    class="w-full relative bg-[#fff] overflow-hidden flex flex-col items-center justify-between p-2.5 box-border gap-0 min-h-[1080px] leading-[normal] tracking-[normal]"
  >
    <Header />
    <main
      class="self-stretch overflow-hidden flex flex-col items-center justify-start max-w-full mq1025:gap-[30px]"
    >
      <div
        class="overflow-hidden flex flex-col items-center justify-start py-2.5 px-0 box-border max-w-full"
      >
        <div
          class="w-[780px] h-[778px] flex flex-col items-end justify-start gap-[107.2px] max-w-full mq450:h-auto mq450:gap-[27px] mq1025:gap-[54px]"
        >
          <section
            class="flex flex-col items-end justify-start gap-[47.1px] max-w-full text-center text-2xl text-[#000] font-[ABeeZee] mq450:gap-6"
          >
            <div
              class="w-[780px] flex flex-row items-start justify-center py-0 pl-[29px] pr-5 box-border max-w-full"
            >
              <div
                class="w-[305px] flex flex-row items-start justify-between gap-5"
              >
                <div
                  class="h-[116px] w-[72px] flex flex-col items-center justify-center gap-2.5"
                >
                  <img
                    class="w-16 h-16 relative"
                    loading="lazy"
                    alt=""
                    src="/rfid-icon.svg"
                  />
                  <h3
                    class="m-0 relative text-[length:inherit] font-normal font-[inherit] mq450:text-[19px]"
                  >
                    RFID System
                  </h3>
                </div>
                <div
                  class="h-[131.3px] w-[72px] flex flex-col items-center justify-center font-[Roboto]"
                >
                  <img
                    class="w-16 h-16 relative overflow-hidden shrink-0"
                    loading="lazy"
                    alt=""
                    src="/productionanalytics-1.svg"
                  />
                  <div class="relative mq450:text-[19px]">
                    <p class="m-0">Production</p>
                    <p class="m-0">Analytics</p>
                  </div>
                </div>
              </div>
            </div>
            <div
              class="w-[780px] flex flex-row items-start justify-between gap-5 max-w-full mq450:flex-wrap mq450:justify-center"
            >
              <div
                class="flex flex-col items-start justify-start pt-[4.3px] px-0 pb-0"
              >
                <div
                  class="w-[168px] h-[159.8px] flex flex-col items-center justify-center gap-[18px]"
                >
                  <img
                    class="w-16 h-16 relative"
                    loading="lazy"
                    alt=""
                    src="/wrist-strap-icon.svg"
                  />
                  <div class="self-stretch relative mq450:text-[19px]">
                    <p class="m-0">Wrist Strap</p>
                    <p class="m-0">Monitor</p>
                  </div>
                </div>
              </div>
              <div
                class="h-[188.2px] w-[168px] flex flex-col items-center justify-start gap-3"
              >
                <img
                  class="w-16 relative max-h-full object-cover"
                  loading="lazy"
                  alt=""
                  src="/led-fpc-assembling-machine@2x.png"
                />
                <div class="self-stretch relative mq450:text-[19px]">
                  <p class="m-0">LED FPC</p>
                  <p class="m-0">Assembling Machine</p>
                </div>
              </div>
            </div>
          </section>
          <section
            class="flex flex-col items-start justify-start gap-[41.6px] max-w-full text-center text-2xl text-[#000] font-[ABeeZee] mq450:gap-[21px]"
          >
            <div
              class="w-[769px] flex flex-row items-start justify-between gap-5 max-w-full mq450:flex-wrap"
            >
              <div
                class="h-[111.6px] w-[168px] flex flex-col items-center justify-center gap-1.5"
              >
                <img
                  class="w-16 relative max-h-full object-cover"
                  loading="lazy"
                  alt=""
                  src="/aoi-icon@2x.png"
                />
                <h3
                  class="m-0 self-stretch relative text-[length:inherit] font-normal font-[inherit] mq450:text-[19px]"
                >
                  AOI LED FPC
                </h3>
              </div>
              <div
                class="h-[114.9px] w-[168px] flex flex-col items-center justify-start gap-[9px]"
              >
                <img
                  class="w-16 h-16 relative overflow-hidden shrink-0"
                  loading="lazy"
                  alt=""
                  src="/jig-1.svg"
                />
                <h3
                  class="m-0 self-stretch relative text-[length:inherit] font-normal font-[inherit] mq450:text-[19px]"
                >
                  JIG Monitor
                </h3>
              </div>
            </div>
            <div
              class="w-[769px] flex flex-row items-start justify-center py-0 pl-5 pr-[27px] box-border max-w-full"
            >
              <div
                class="w-[414px] flex flex-row items-start justify-between gap-5"
              >
                <div
                  class="h-[112.7px] w-[168px] flex flex-col items-center justify-start gap-[7px]"
                >
                  <img
                    class="w-16 relative max-h-full object-cover"
                    loading="lazy"
                    alt=""
                    src="/agv-icon@2x.png"
                  />
                  <h3
                    class="m-0 self-stretch relative text-[length:inherit] font-normal font-[inherit] mq450:text-[19px]"
                  >
                    AGV System
                  </h3>
                </div>
                <div
                  class="h-[147.7px] w-[168px] flex flex-col items-center justify-center gap-[7px]"
                >
                  <img
                    class="w-16 h-16 relative overflow-hidden shrink-0"
                    loading="lazy"
                    alt=""
                    src="/thermometer-1.svg"
                  />
                  <div class="self-stretch relative mq450:text-[19px]">
                    Thermometer Monitor
                  </div>
                </div>
              </div>
            </div>
          </section>
        </div>
      </div>
    </main>
    <Footer />
  </div>
</template>
<script setup lang="ts">
  import Header from "../components/Header.vue"
  import Footer from "../components/Footer.vue"
</script>
